"""HU-01 · Disponibilidad efectiva y reserva preferencial de 30 minutos.

Contrato en `specs/api.md`; reglas BR-01–BR-04/11/13–15; criterios AC-01/02/03/07/13.
Usa la primitiva compartida `allocation_transaction` (sesión nueva) y captura
`Clock.now()` una sola vez por operación. La disponibilidad nunca muta la base:
una reserva pendiente vencida se ignora en lectura y se normaliza dentro del
bloqueo antes de asignar.

D-03 (placa con estadía abierta) y D-04 (normalización de placa) se aplican tal
como están propuestas en `docs/decisions.md`; siguen pendientes de confirmación
de Product/Spec y se revisan en el PR de la historia.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import segno
from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy import delete, exists, func, select, update
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from .auth import require_roles, same_origin
from .db import allocation_transaction, get_session
from .errors import AppError
from .models import Allocation, Reservation, Space, Stay
from .security import new_token, token_digest

ROOT = Path(__file__).parent
templates = Jinja2Templates(directory=str(ROOT / "templates"))

RESERVATION_MINUTES = 30
PLATE_PATTERN = re.compile(r"[A-Z0-9-]{2,12}")
PANAMA = ZoneInfo("America/Panama")

router = APIRouter(prefix="/api", tags=["reservas"])
views = APIRouter(tags=["reservas"])


def local_time(value: datetime) -> str:
    return value.astimezone(PANAMA).strftime("%d/%m/%Y %H:%M")


def normalize_plate(raw: str) -> str:
    """D-04: mayúsculas y recorte exterior; nunca elimina guiones internos."""
    plate = (raw or "").strip().upper()
    if not PLATE_PATTERN.fullmatch(plate):
        raise AppError(422, "VALIDATION_ERROR",
                       "La placa requiere de 2 a 12 caracteres A–Z, 0–9 o guion")
    return plate


def normalize_customer_name(raw: str) -> str:
    name = " ".join((raw or "").split())
    if not 2 <= len(name) <= 80:
        raise AppError(422, "VALIDATION_ERROR", "El nombre requiere entre 2 y 80 caracteres")
    return name


def parse_scheduled_at(raw: str) -> datetime:
    try:
        value = datetime.fromisoformat((raw or "").replace("Z", "+00:00"))
    except ValueError as exc:
        raise AppError(422, "VALIDATION_ERROR", "Selecciona una fecha y hora válidas") from exc
    if value.tzinfo is None:
        value = value.replace(tzinfo=PANAMA)
    return value.astimezone(ZoneInfo("UTC"))


def effective_availability(session: Session, now: datetime) -> dict:
    """Capacidad derivada; ignora reservas vencidas sin escribir en la base."""
    totals = dict(session.execute(
        select(Space.category, func.count()).group_by(Space.category)).all())
    preferential_total = int(totals.get("preferential", 0))
    general_total = int(totals.get("general", 0))
    reservation_start = func.coalesce(Reservation.scheduled_at, Reservation.created_at)
    reserved = session.scalar(
        select(func.count()).select_from(Reservation)
        .join(Space, Space.code == Reservation.space_id)
        .where(Reservation.status == "pending",
               reservation_start <= now,
               Reservation.expires_at > now,
               Space.category == "preferential")) or 0
    occupied = dict(session.execute(
        select(Space.category, func.count()).select_from(Allocation)
        .join(Stay, Stay.id == Allocation.stay_id)
        .join(Space, Space.code == Allocation.space_id)
        .where(Stay.status == "open")
        .group_by(Space.category)).all())
    return {
        "as_of": now,
        "preferential": {
            "available": max(0, preferential_total - reserved - int(occupied.get("preferential", 0))),
            "total": preferential_total,
        },
        "general": {
            "available": max(0, general_total - int(occupied.get("general", 0))),
            "total": general_total,
        },
    }


def release_expired(session: Session, now: datetime) -> int:
    """Normaliza reservas `pending` vencidas y libera sus asignaciones.

    Debe ejecutarse dentro de `allocation_transaction`: el UNIQUE parcial de placa
    y la PK de `allocations` no expresan el paso del tiempo por sí solos.
    """
    stale = session.scalars(select(Reservation.id).where(
        Reservation.status == "pending", Reservation.expires_at <= now)).all()
    if not stale:
        return 0
    session.execute(delete(Allocation).where(Allocation.reservation_id.in_(stale)))
    session.execute(update(Reservation)
                    .where(Reservation.id.in_(stale), Reservation.status == "pending")
                    .values(status="expired"))
    return len(stale)


def create_reservation(session: Session, now: datetime, raw_name: str = "Cliente demo", raw_plate: str = "",
                       raw_scheduled_at: str | None = None) -> dict:
    """Crea reserva + asignación en una sola transacción serializada.

    El código privado se devuelve solo aquí; en la base queda su digest.
    """
    # Compatibilidad interna: llamadas previas pasaban solo la placa como tercer argumento.
    if not raw_plate:
        raw_plate, raw_name = raw_name, "Cliente demo"
    plate = normalize_plate(raw_plate)
    customer_name = normalize_customer_name(raw_name)
    scheduled_at = parse_scheduled_at(raw_scheduled_at) if raw_scheduled_at else now
    expires_at = scheduled_at + timedelta(minutes=RESERVATION_MINUTES)
    try:
        with allocation_transaction(session):
            release_expired(session, now)
            if session.scalar(select(exists().where(
                    Stay.plate == plate, Stay.status == "open"))):
                raise AppError(409, "PLATE_BUSY", "La placa tiene una estadía abierta")
            if session.scalar(select(exists().where(
                    Reservation.plate == plate, Reservation.status == "pending"))):
                raise AppError(409, "PLATE_BUSY", "La placa ya tiene una reserva pendiente")
            reservation_start = func.coalesce(Reservation.scheduled_at, Reservation.created_at)
            space_code = session.scalar(
                select(Space.code)
                .where(Space.category == "preferential",
                       ~exists().where(Allocation.space_id == Space.code),
                       ~exists().where(Reservation.space_id == Space.code,
                                       Reservation.status == "pending",
                                       reservation_start < expires_at,
                                       Reservation.expires_at > scheduled_at))
                .order_by(Space.code)
                .limit(1))
            if space_code is None:
                raise AppError(409, "CATEGORY_FULL",
                               "No quedan espacios preferenciales disponibles")
            private_code = new_token()
            reservation = Reservation(plate=plate, customer_name=customer_name, space_id=space_code, status="pending",
                                      token_hash=token_digest(private_code), access_code=private_code,
                                      created_at=now, scheduled_at=scheduled_at, expires_at=expires_at)
            session.add(reservation)
            session.flush()
    except IntegrityError:
        raise AppError(409, "PLATE_BUSY",
                       "La placa o el espacio ya están asignados") from None
    except OperationalError:
        raise AppError(503, "DATABASE_BUSY",
                       "La base está ocupada; vuelve a intentarlo") from None
    return {"status": "pending", "space_code": space_code, "plate": plate,
            "customer_name": customer_name, "scheduled_at": scheduled_at,
            "created_at": now, "expires_at": expires_at, "private_code": private_code}


def qr_svg(private_code: str) -> str:
    """QR del código privado. Sin placa, sin nombre y sin URL con secretos."""
    return segno.make(private_code, error="m").svg_inline(scale=5, border=3)


class ReservationBody(BaseModel):
    customer_name: str = Field(min_length=2, max_length=80)
    plate: str = Field(min_length=1, max_length=40)
    scheduled_at: str = Field(min_length=16, max_length=40)


def _no_store(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@router.get("/availability")
def availability(request: Request, response: Response,
               session: Session = Depends(get_session)):
    data = effective_availability(session, request.app.state.clock.now())
    _no_store(response)
    return data


@router.post("/reservations", status_code=201, dependencies=[Depends(same_origin), Depends(require_roles("client", "admin"))])
def reserve(body: ReservationBody, request: Request, response: Response,
            session: Session = Depends(get_session)):
    result = create_reservation(session, request.app.state.clock.now(), body.customer_name, body.plate, body.scheduled_at)
    _no_store(response)
    return result


@views.get("/reservar", response_class=HTMLResponse, dependencies=[Depends(require_roles("client", "admin"))])
def reserve_page(request: Request, session: Session = Depends(get_session)):
    now = request.app.state.clock.now()
    return templates.TemplateResponse(
        request=request, name="reservations/availability.html",
        context={"availability": effective_availability(session, now), "as_of": local_time(now),
                 "local": local_time, "plate": "", "customer_name": "", "scheduled_at": "", "error": None})


@views.post("/reservar", response_class=HTMLResponse, dependencies=[Depends(same_origin), Depends(require_roles("client", "admin"))])
def reserve_submit(request: Request, customer_name: str = Form(default=""), plate: str = Form(default=""),
                   scheduled_at: str = Form(default=""),
                   session: Session = Depends(get_session)):
    now = request.app.state.clock.now()
    try:
        result = create_reservation(session, now, customer_name, plate, scheduled_at)
    except AppError as exc:
        if exc.status not in {409, 422}:
            raise
        return _no_store(templates.TemplateResponse(
            request=request, name="reservations/availability.html", status_code=exc.status,
            context={"availability": effective_availability(session, now),
                     "as_of": local_time(now), "local": local_time,
                     "plate": plate, "customer_name": customer_name, "scheduled_at": scheduled_at, "error": exc.message}))
    return _no_store(templates.TemplateResponse(
        request=request, name="reservations/created.html",
        context={"reservation": result, "qr_svg": qr_svg(result["private_code"]),
                 "created": local_time(result["created_at"]),
                 "scheduled": local_time(result["scheduled_at"]),
                 "expires": local_time(result["expires_at"])}))


# --- HU-02 · consulta y cancelación privadas por código -----------------------

STATUS_LABELS = {"pending": "Vigente", "expired": "Vencida",
                 "cancelled": "Cancelada", "used": "Utilizada"}


def effective_status(reservation: Reservation, now: datetime) -> str:
    """Una reserva pendiente vencida se interpreta vencida sin escribir."""
    if reservation.status == "pending" and reservation.expires_at <= now:
        return "expired"
    return reservation.status


def reservation_payload(reservation: Reservation, now: datetime) -> dict:
    status = effective_status(reservation, now)
    remaining = max(0, int((reservation.expires_at - now).total_seconds())) if status == "pending" else 0
    return {"status": status, "status_label": STATUS_LABELS[status],
            "plate": reservation.plate, "customer_name": reservation.customer_name,
            "space_code": reservation.space_id, "scheduled_at": reservation.scheduled_at or reservation.created_at,
            "created_at": reservation.created_at, "expires_at": reservation.expires_at,
            "cancelled_at": reservation.cancelled_at, "used_at": reservation.used_at,
            "remaining_seconds": remaining}


def _code_digest(raw: str) -> str:
    code = (raw or "").strip()
    if not 1 <= len(code) <= 128:
        raise AppError(404, "NOT_FOUND", "No encontramos una reserva con ese código")
    return token_digest(code)


def lookup_reservation(session: Session, now: datetime, raw_code: str) -> dict:
    """Solo devuelve la reserva cuyo código privado coincide; sin enumeración."""
    reservation = session.scalar(select(Reservation).where(
        Reservation.token_hash == _code_digest(raw_code)))
    if reservation is None:
        raise AppError(404, "NOT_FOUND", "No encontramos una reserva con ese código")
    return reservation_payload(reservation, now)


def cancel_reservation(session: Session, now: datetime, raw_code: str) -> dict:
    """D-05: repetir la cancelación devuelve el mismo estado terminal.

    Usada responde 409; vencida informa su estado efectivo sin reescribirlo.
    """
    digest = _code_digest(raw_code)
    try:
        with allocation_transaction(session):
            release_expired(session, now)
            reservation = session.scalar(select(Reservation).where(
                Reservation.token_hash == digest))
            if reservation is None:
                raise AppError(404, "NOT_FOUND", "No encontramos una reserva con ese código")
            if reservation.status == "used":
                raise AppError(409, "RESERVATION_USED", "La reserva ya se utilizó en garita")
            if reservation.status == "cancelled":
                return reservation_payload(reservation, now)
            if reservation.status == "expired":
                return reservation_payload(reservation, now)
            reservation.status = "cancelled"
            reservation.cancelled_at = now
            session.execute(delete(Allocation).where(
                Allocation.reservation_id == reservation.id))
            payload = reservation_payload(reservation, now)
    except OperationalError:
        raise AppError(503, "DATABASE_BUSY", "La base está ocupada; vuelve a intentarlo") from None
    return payload


class CodeBody(BaseModel):
    private_code: str = Field(min_length=1, max_length=128)


@router.post("/reservations/lookup", dependencies=[Depends(require_roles("client", "admin"))])
def lookup(body: CodeBody, request: Request, response: Response,
           session: Session = Depends(get_session)):
    payload = lookup_reservation(session, request.app.state.clock.now(), body.private_code)
    _no_store(response)
    return payload


@router.post("/reservations/cancel", dependencies=[Depends(same_origin), Depends(require_roles("client", "admin"))])
def cancel(body: CodeBody, request: Request, response: Response,
           session: Session = Depends(get_session)):
    payload = cancel_reservation(session, request.app.state.clock.now(), body.private_code)
    _no_store(response)
    return payload


def _status_context(payload: dict, now: datetime, error=None, code=""):
    return {"reservation": payload, "error": error, "code": code,
            "created": local_time(payload["created_at"]),
            "expires": local_time(payload["expires_at"]),
            "cancelled": local_time(payload["cancelled_at"]) if payload["cancelled_at"] else None,
            "remaining": -(-payload["remaining_seconds"] // 60),
            "as_of": local_time(now), "local": local_time}


@views.get("/mi-reserva", response_class=HTMLResponse, dependencies=[Depends(require_roles("client", "admin"))])
def lookup_page(request: Request, response: Response):
    _no_store(response)
    return templates.TemplateResponse(
        request=request, name="reservations/lookup.html",
        context={"code": "", "error": None})


@views.post("/mi-reserva", response_class=HTMLResponse, dependencies=[Depends(same_origin), Depends(require_roles("client", "admin"))])
def lookup_submit(request: Request, private_code: str = Form(default=""),
                  session: Session = Depends(get_session)):
    now = request.app.state.clock.now()
    try:
        payload = lookup_reservation(session, now, private_code)
    except AppError as exc:
        if exc.status != 404:
            raise
        return _no_store(templates.TemplateResponse(
            request=request, name="reservations/lookup.html", status_code=404,
            context={"code": "", "error": exc.message}))
    return _no_store(templates.TemplateResponse(
        request=request, name="reservations/status.html",
        context=_status_context(payload, now, code=private_code)))


@views.post("/mi-reserva/cancelar", response_class=HTMLResponse,
            dependencies=[Depends(same_origin), Depends(require_roles("client", "admin"))])
def cancel_submit(request: Request, private_code: str = Form(default=""),
                  session: Session = Depends(get_session)):
    now = request.app.state.clock.now()
    try:
        payload = cancel_reservation(session, now, private_code)
    except AppError as exc:
        if exc.status not in {404, 409}:
            raise
        if exc.status == 404:
            return _no_store(templates.TemplateResponse(
                request=request, name="reservations/lookup.html", status_code=404,
                context={"code": "", "error": exc.message}))
        payload = lookup_reservation(session, now, private_code)
        return _no_store(templates.TemplateResponse(
            request=request, name="reservations/status.html", status_code=409,
            context=_status_context(payload, now, error=exc.message, code=private_code)))
    return _no_store(templates.TemplateResponse(
        request=request, name="reservations/status.html",
        context=_status_context(payload, now, code=private_code)))
