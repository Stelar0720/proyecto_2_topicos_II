"""HU-03 · Ingreso en garita: reserva convertida en estadía y espontáneo general.

Contrato en `specs/api.md`; reglas BR-05–BR-12/14/16/17; criterios AC-05/06/07/08/13.
Toda escritura ocurre en una `allocation_transaction` con sesión nueva: libera
reservas vencidas, valida placa/estado y escribe estadía, asignación y ticket en un
solo commit. El ticket se entrega una vez; en la base queda su digest.

El personal de garita usa las sesiones existentes (`current_staff` / `require_roles`);
la comprobación de la placa es manual, en garita.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy import delete, exists, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from .auth import current_staff, require_roles, same_origin
from .db import allocation_transaction, get_session
from .errors import AppError
from .models import Allocation, Reservation, Space, Staff, Stay
from .reservations import (effective_availability, effective_status, local_time,
                           normalize_plate, parse_scheduled_at, qr_svg, release_expired)
from .security import new_token, token_digest

ROOT = Path(__file__).parent
templates = Jinja2Templates(directory=str(ROOT / "templates"))

GARITA_ROLES = ("admin",)
router = APIRouter(prefix="/api", tags=["garita"])
views = APIRouter(tags=["garita"])


def _no_store(response):
    response.headers["Cache-Control"] = "no-store"
    return response


def _stay_payload(stay: Stay, ticket_code: str, now: datetime) -> dict:
    return {"status": stay.status, "stay_id": stay.id, "space_code": stay.space_id,
            "plate": stay.plate, "entered_at": stay.entered_at, "as_of": now,
            "ticket_code": ticket_code}


def enter_with_reservation(session: Session, now: datetime, raw_code: str,
                           raw_plate: str) -> dict:
    """Convierte una reserva vigente en estadía abierta de forma atómica."""
    plate = normalize_plate(raw_plate)
    code = (raw_code or "").strip()
    if not 1 <= len(code) <= 128:
        raise AppError(404, "NOT_FOUND", "No encontramos una reserva con ese código")
    digest = token_digest(code)
    try:
        with allocation_transaction(session):
            release_expired(session, now)
            reservation = session.scalar(select(Reservation).where(
                Reservation.token_hash == digest))
            if reservation is None:
                raise AppError(404, "NOT_FOUND", "No encontramos una reserva con ese código")
            status = effective_status(reservation, now)
            if status == "cancelled":
                raise AppError(409, "RESERVATION_CANCELLED", "La reserva fue cancelada")
            if status == "expired":
                raise AppError(409, "RESERVATION_EXPIRED", "La reserva venció sin ingreso")
            if status == "used":
                raise AppError(409, "RESERVATION_USED", "La reserva ya se utilizó")
            scheduled_at = reservation.scheduled_at or reservation.created_at
            if now < scheduled_at:
                raise AppError(409, "RESERVATION_NOT_READY",
                               "La reserva aún no está vigente para registrar el ingreso")
            if reservation.plate != plate:
                raise AppError(409, "PLATE_MISMATCH", "La placa no corresponde a la reserva")
            if session.scalar(select(exists().where(
                    Stay.plate == plate, Stay.status == "open"))):
                raise AppError(409, "PLATE_BUSY", "La placa ya tiene una estadía abierta")
            allocation = session.get(Allocation, reservation.space_id)
            if allocation is not None and allocation.reservation_id != reservation.id:
                raise AppError(409, "CATEGORY_FULL", "El espacio ya está ocupado")
            # El QR de reserva continúa siendo el QR de salida de esta misma visita.
            ticket_code = code
            stay = Stay(plate=plate, space_id=reservation.space_id,
                        reservation_id=reservation.id,
                        ticket_hash=token_digest(ticket_code), access_code=ticket_code,
                        status="open", entered_at=now)
            session.add(stay)
            session.flush()
            if allocation is not None:
                session.execute(delete(Allocation).where(
                    Allocation.space_id == reservation.space_id,
                    Allocation.reservation_id == reservation.id))
            session.add(Allocation(space_id=reservation.space_id, plate=plate, stay_id=stay.id))
            reservation.status = "used"
            reservation.used_at = now
            payload = _stay_payload(stay, ticket_code, now)
    except IntegrityError:
        raise AppError(409, "PLATE_BUSY",
                       "La placa o el espacio ya están asignados") from None
    except OperationalError:
        raise AppError(503, "DATABASE_BUSY", "La base está ocupada; vuelve a intentarlo") from None
    return payload


def enter_walk_in(session: Session, now: datetime, raw_plate: str) -> dict:
    """Asigna un general libre a un espontáneo; nunca un preferencial."""
    plate = normalize_plate(raw_plate)
    try:
        with allocation_transaction(session):
            release_expired(session, now)
            if session.scalar(select(exists().where(
                    Stay.plate == plate, Stay.status == "open"))):
                raise AppError(409, "PLATE_BUSY", "La placa ya tiene una estadía abierta")
            if session.scalar(select(exists().where(
                    Reservation.plate == plate, Reservation.status == "pending"))):
                raise AppError(409, "PLATE_BUSY", "La placa tiene una reserva pendiente")
            space_code = session.scalar(
                select(Space.code)
                .where(Space.category == "general",
                       ~exists().where(Allocation.space_id == Space.code))
                .order_by(Space.code)
                .limit(1))
            if space_code is None:
                raise AppError(409, "CATEGORY_FULL", "No quedan espacios generales disponibles")
            ticket_code = new_token()
            stay = Stay(plate=plate, space_id=space_code, reservation_id=None,
                        ticket_hash=token_digest(ticket_code), access_code=ticket_code,
                        status="open", entered_at=now)
            session.add(stay)
            session.flush()
            session.add(Allocation(space_id=space_code, plate=plate, stay_id=stay.id))
            payload = _stay_payload(stay, ticket_code, now)
    except IntegrityError:
        raise AppError(409, "PLATE_BUSY",
                       "La placa o el espacio ya están asignados") from None
    except OperationalError:
        raise AppError(503, "DATABASE_BUSY", "La base está ocupada; vuelve a intentarlo") from None
    return payload


class EntryBody(BaseModel):
    plate: str = Field(min_length=1, max_length=40)
    entered_at: str | None = Field(default=None, max_length=40)


class ReservationEntryBody(BaseModel):
    private_code: str = Field(min_length=1, max_length=128)
    plate: str = Field(min_length=1, max_length=40)
    entered_at: str | None = Field(default=None, max_length=40)


def _open_session(request: Request) -> Session:
    """Sesión nueva para la asignación: la de la petición ya leyó la sesión del personal."""
    return Session(request.app.state.engine)


@router.post("/entries/reservation", status_code=201,
             dependencies=[Depends(same_origin)])
def entry_reservation(body: ReservationEntryBody, request: Request, response: Response,
                      staff: Staff = Depends(require_roles(*GARITA_ROLES))):
    with _open_session(request) as session:
        entered_at = parse_scheduled_at(body.entered_at) if body.entered_at else request.app.state.clock.now()
        payload = enter_with_reservation(session, entered_at,
                                         body.private_code, body.plate)
    _no_store(response)
    return payload


@router.post("/entries/walk-in", status_code=201, dependencies=[Depends(same_origin)])
def entry_walk_in(body: EntryBody, request: Request, response: Response,
                  staff: Staff = Depends(require_roles(*GARITA_ROLES))):
    with _open_session(request) as session:
        entered_at = parse_scheduled_at(body.entered_at) if body.entered_at else request.app.state.clock.now()
        payload = enter_walk_in(session, entered_at, body.plate)
    _no_store(response)
    return payload


def _optional_staff(request: Request, session: Session) -> Staff | None:
    try:
        return current_staff(request, session)
    except AppError:
        return None


def _denied(request: Request, staff: Staff | None):
    """401 sin sesión, 403 con rol que no opera garita; nunca JSON en la vista."""
    if staff is None:
        return _no_store(templates.TemplateResponse(
            request=request, name="entries/unauthorized.html", status_code=401,
            context={"staff": None}))
    if staff.role not in GARITA_ROLES:
        return _no_store(templates.TemplateResponse(
            request=request, name="entries/forbidden.html", status_code=403,
            context={"staff": staff}))
    return None


def _garita_page(request: Request, session: Session, staff: Staff, *,
                 error=None, status: int = 200, code: str = "", plate: str = ""):
    now = request.app.state.clock.now()
    return _no_store(templates.TemplateResponse(
        request=request, name="entries/garita.html", status_code=status,
        context={"staff": staff, "error": error, "as_of": local_time(now),
                 "availability": effective_availability(session, now),
                 "code": code, "plate": plate}))


def _ticket_page(request: Request, payload: dict):
    return _no_store(templates.TemplateResponse(
        request=request, name="entries/ticket.html",
        context={"entry": payload, "entered": local_time(payload["entered_at"]),
                 "qr_svg": qr_svg(payload["ticket_code"])}))


@views.get("/garita", response_class=HTMLResponse)
def garita_page(request: Request, session: Session = Depends(get_session)):
    staff = _optional_staff(request, session)
    denied = _denied(request, staff)
    if denied is not None:
        return denied
    return _garita_page(request, session, staff)


@views.post("/garita/reserva", response_class=HTMLResponse,
            dependencies=[Depends(same_origin)])
def garita_reservation(request: Request, private_code: str = Form(default=""),
                       plate: str = Form(default=""),
                       entered_at: str = Form(default=""),
                       session: Session = Depends(get_session)):
    staff = _optional_staff(request, session)
    denied = _denied(request, staff)
    if denied is not None:
        return denied
    try:
        now = parse_scheduled_at(entered_at) if entered_at else request.app.state.clock.now()
        with _open_session(request) as assignment:
            payload = enter_with_reservation(assignment, now, private_code, plate)
    except AppError as exc:
        if exc.status not in {404, 409, 422}:
            raise
        return _garita_page(request, session, staff, error=exc.message,
                            status=exc.status, code=private_code, plate=plate)
    return _ticket_page(request, payload)


@views.post("/garita/espontaneo", response_class=HTMLResponse,
            dependencies=[Depends(same_origin)])
def garita_walk_in(request: Request, plate: str = Form(default=""),
                   entered_at: str = Form(default=""),
                   session: Session = Depends(get_session)):
    staff = _optional_staff(request, session)
    denied = _denied(request, staff)
    if denied is not None:
        return denied
    try:
        now = parse_scheduled_at(entered_at) if entered_at else request.app.state.clock.now()
        with _open_session(request) as assignment:
            payload = enter_walk_in(assignment, now, plate)
    except AppError as exc:
        if exc.status not in {409, 422}:
            raise
        return _garita_page(request, session, staff, error=exc.message,
                            status=exc.status, plate=plate)
    return _ticket_page(request, payload)
