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

from .auth import same_origin
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


def effective_availability(session: Session, now: datetime) -> dict:
    """Capacidad derivada; ignora reservas vencidas sin escribir en la base."""
    totals = dict(session.execute(
        select(Space.category, func.count()).group_by(Space.category)).all())
    preferential_total = int(totals.get("preferential", 0))
    general_total = int(totals.get("general", 0))
    reserved = session.scalar(
        select(func.count()).select_from(Allocation)
        .join(Reservation, Reservation.id == Allocation.reservation_id)
        .join(Space, Space.code == Allocation.space_id)
        .where(Reservation.status == "pending",
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


def create_reservation(session: Session, now: datetime, raw_plate: str) -> dict:
    """Crea reserva + asignación en una sola transacción serializada.

    El código privado se devuelve solo aquí; en la base queda su digest.
    """
    plate = normalize_plate(raw_plate)
    expires_at = now + timedelta(minutes=RESERVATION_MINUTES)
    try:
        with allocation_transaction(session):
            release_expired(session, now)
            if session.scalar(select(exists().where(
                    Stay.plate == plate, Stay.status == "open"))):
                raise AppError(409, "PLATE_BUSY", "La placa tiene una estadía abierta")
            if session.scalar(select(exists().where(
                    Reservation.plate == plate, Reservation.status == "pending"))):
                raise AppError(409, "PLATE_BUSY", "La placa ya tiene una reserva pendiente")
            space_code = session.scalar(
                select(Space.code)
                .where(Space.category == "preferential",
                       ~exists().where(Allocation.space_id == Space.code))
                .order_by(Space.code)
                .limit(1))
            if space_code is None:
                raise AppError(409, "CATEGORY_FULL",
                               "No quedan espacios preferenciales disponibles")
            private_code = new_token()
            reservation = Reservation(plate=plate, space_id=space_code, status="pending",
                                      token_hash=token_digest(private_code),
                                      created_at=now, expires_at=expires_at)
            session.add(reservation)
            session.flush()
            session.add(Allocation(space_id=space_code, plate=plate,
                                   reservation_id=reservation.id))
    except IntegrityError:
        raise AppError(409, "PLATE_BUSY",
                       "La placa o el espacio ya están asignados") from None
    except OperationalError:
        raise AppError(503, "DATABASE_BUSY",
                       "La base está ocupada; vuelve a intentarlo") from None
    return {"status": "pending", "space_code": space_code, "plate": plate,
            "created_at": now, "expires_at": expires_at, "private_code": private_code}


def qr_svg(private_code: str) -> str:
    """QR del código privado. Sin placa, sin nombre y sin URL con secretos."""
    return segno.make(private_code, error="m").svg_inline(scale=5, border=3)


class ReservationBody(BaseModel):
    plate: str = Field(min_length=1, max_length=40)


def _no_store(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@router.get("/availability")
def availability(request: Request, response: Response,
               session: Session = Depends(get_session)):
    data = effective_availability(session, request.app.state.clock.now())
    _no_store(response)
    return data


@router.post("/reservations", status_code=201, dependencies=[Depends(same_origin)])
def reserve(body: ReservationBody, request: Request, response: Response,
            session: Session = Depends(get_session)):
    result = create_reservation(session, request.app.state.clock.now(), body.plate)
    _no_store(response)
    return result


@views.get("/reservar", response_class=HTMLResponse)
def reserve_page(request: Request, session: Session = Depends(get_session)):
    now = request.app.state.clock.now()
    return templates.TemplateResponse(
        request=request, name="reservations/availability.html",
        context={"availability": effective_availability(session, now), "as_of": local_time(now),
                 "local": local_time, "plate": "", "error": None})


@views.post("/reservar", response_class=HTMLResponse, dependencies=[Depends(same_origin)])
def reserve_submit(request: Request, plate: str = Form(default=""),
                   session: Session = Depends(get_session)):
    now = request.app.state.clock.now()
    try:
        result = create_reservation(session, now, plate)
    except AppError as exc:
        if exc.status not in {409, 422}:
            raise
        return _no_store(templates.TemplateResponse(
            request=request, name="reservations/availability.html", status_code=exc.status,
            context={"availability": effective_availability(session, now),
                     "as_of": local_time(now), "local": local_time,
                     "plate": plate, "error": exc.message}))
    return _no_store(templates.TemplateResponse(
        request=request, name="reservations/created.html",
        context={"reservation": result, "qr_svg": qr_svg(result["private_code"]),
                 "created": local_time(result["created_at"]),
                 "expires": local_time(result["expires_at"])}))
