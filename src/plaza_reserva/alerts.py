"""HU-05 - Alerta de estadias abiertas de mas de 24 horas (T-05A).

Contrato propuesto en specs/api.md; reglas BR-24..BR-28; AC-12/13.
Solo lectura: no modifica datos, sin recargo ni liberacion.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import current_staff, require_roles
from .db import get_session
from .errors import AppError
from .models import Staff, Stay
from .reservations import local_time

ROOT = Path(__file__).parent
templates = Jinja2Templates(directory=str(ROOT / "templates"))

ALERT_ROLES = ("admin",)
ALERT_THRESHOLD = timedelta(hours=24)

router = APIRouter(prefix="/api", tags=["alertas"])
views = APIRouter(tags=["alertas"])


def _no_store(response):
    response.headers["Cache-Control"] = "no-store"
    return response


def long_stays(session: Session, now: datetime) -> dict:
    """Estadias abiertas con duracion estrictamente mayor a 24 horas."""
    cutoff = now - ALERT_THRESHOLD
    stays = session.scalars(
        select(Stay).where(Stay.status == "open", Stay.entered_at < cutoff)
        .order_by(Stay.entered_at, Stay.space_id)).all()
    items = []
    for stay in stays:
        elapsed = int((now - stay.entered_at).total_seconds())
        items.append({
            "stay_id": stay.id,
            "plate": stay.plate,
            "space_code": stay.space_id,
            "entered_at": stay.entered_at,
            "elapsed_seconds": elapsed,
        })
    return {"as_of": now, "items": items}


@router.get("/alerts/long-stays")
def alerts_long_stays(request: Request, response: Response,
                      session: Session = Depends(get_session),
                      staff: Staff = Depends(require_roles(*ALERT_ROLES))):
    payload = long_stays(session, request.app.state.clock.now())
    _no_store(response)
    return payload


def _optional_staff(request: Request, session: Session) -> Staff | None:
    try:
        return current_staff(request, session)
    except AppError:
        return None


def _denied(request: Request, staff: Staff | None):
    if staff is None:
        return _no_store(templates.TemplateResponse(
            request=request, name="alerts/unauthorized.html", status_code=401,
            context={"staff": None}))
    if staff.role not in ALERT_ROLES:
        return _no_store(templates.TemplateResponse(
            request=request, name="alerts/forbidden.html", status_code=403,
            context={"staff": staff}))
    return None


@views.get("/vigilancia", response_class=HTMLResponse)
def vigilancia_page(request: Request, session: Session = Depends(get_session)):
    staff = _optional_staff(request, session)
    denied = _denied(request, staff)
    if denied is not None:
        return denied
    now = request.app.state.clock.now()
    payload = long_stays(session, now)
    for item in payload["items"]:
        item["entered_local"] = local_time(item["entered_at"])
        item["elapsed_hours"] = item["elapsed_seconds"] // 3600
        item["elapsed_minutes"] = (item["elapsed_seconds"] % 3600) // 60
    return _no_store(templates.TemplateResponse(
        request=request, name="alerts/vigilancia.html",
        context={"staff": staff, "as_of": local_time(now), "items": payload["items"]}))
