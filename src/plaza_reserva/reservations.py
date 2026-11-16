"""HU-01 · Disponibilidad efectiva de espacios preferenciales y generales.

Contrato en `specs/api.md`; reglas BR-01–BR-04/11/13–15; criterios AC-01/02/03/07/13.
La disponibilidad nunca muta la base: una reserva pendiente vencida se ignora en
lectura y se normaliza dentro del bloqueo antes de asignar (T-01B).
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .db import get_session
from .models import Allocation, Reservation, Space, Stay

ROOT = Path(__file__).parent
templates = Jinja2Templates(directory=str(ROOT / "templates"))

PANAMA = ZoneInfo("America/Panama")

router = APIRouter(prefix="/api", tags=["reservas"])
views = APIRouter(tags=["reservas"])


def local_time(value: datetime) -> str:
    return value.astimezone(PANAMA).strftime("%d/%m/%Y %H:%M")


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


def _no_store(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@router.get("/availability")
def availability(request: Request, response: Response,
                 session: Session = Depends(get_session)):
    data = effective_availability(session, request.app.state.clock.now())
    _no_store(response)
    return data


@views.get("/reservar", response_class=HTMLResponse)
def reserve_page(request: Request, session: Session = Depends(get_session)):
    now = request.app.state.clock.now()
    return templates.TemplateResponse(
        request=request, name="reservations/availability.html",
        context={"availability": effective_availability(session, now), "as_of": local_time(now),
                 "local": local_time, "plate": "", "error": None})
