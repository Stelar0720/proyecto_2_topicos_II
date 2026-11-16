"""HU-04 - Salida, cotizacion y cobro manual (T-04A/B).

Contrato propuesto en specs/api.md (HU-04); reglas BR-17..BR-23; AC-09/10/11/13.
Cotizacion no muta; cierre es idempotente y atomico con allocation_transaction
(sesion nueva). Importe siempre calculado en servidor con aritmetica entera.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import current_staff, require_roles, same_origin
from .db import get_session
from .errors import AppError
from .models import Staff, Stay
from .reservations import local_time
from .security import token_digest

ROOT = Path(__file__).parent
templates = Jinja2Templates(directory=str(ROOT / "templates"))

SALIDA_ROLES = ("celador", "admin")
MICROSECONDS_PER_MINUTE = 60_000_000
CENTS_PER_MINUTE = 2

router = APIRouter(prefix="/api", tags=["salidas"])
views = APIRouter(tags=["salidas"])


def _no_store(response):
    response.headers["Cache-Control"] = "no-store"
    return response


def quote_amount_cents(entered_at: datetime, now: datetime) -> int:
    """2 centavos por minuto desde entrada real, fraccion al minuto superior.

    Aritmetica entera en microsegundos (AC-09, D-06 propuesta). Duracion cero: 0.
    """
    duration = now - entered_at
    micros = (duration.days * 86_400_000_000
              + duration.seconds * 1_000_000
              + duration.microseconds)
    if micros < 0:
        raise AppError(422, "VALIDATION_ERROR",
                       "El instante de consulta es anterior a la entrada")
    if micros == 0:
        return 0
    minutes = (micros + MICROSECONDS_PER_MINUTE - 1) // MICROSECONDS_PER_MINUTE
    return minutes * CENTS_PER_MINUTE


def _find_stay_by_ticket(session: Session, raw_code: str) -> Stay | None:
    code = (raw_code or "").strip()
    if not 1 <= len(code) <= 128:
        return None
    return session.scalar(select(Stay).where(Stay.ticket_hash == token_digest(code)))


def quote_stay(session: Session, now: datetime, raw_code: str) -> dict:
    stay = _find_stay_by_ticket(session, raw_code)
    if stay is None:
        raise AppError(404, "NOT_FOUND", "No encontramos una estadia con ese ticket")
    if stay.status != "open":
        raise AppError(409, "STAY_CLOSED", "La estadia ya fue cerrada")
    amount = quote_amount_cents(stay.entered_at, now)
    duration_seconds = max(0, int((now - stay.entered_at).total_seconds()))
    return {
        "status": stay.status,
        "stay_id": stay.id,
        "space_code": stay.space_id,
        "plate": stay.plate,
        "entered_at": stay.entered_at,
        "as_of": now,
        "duration_seconds": duration_seconds,
        "amount_cents": amount,
    }


class TicketBody(BaseModel):
    ticket_code: str = Field(min_length=1, max_length=128)


@router.post("/exits/quote", dependencies=[Depends(same_origin)])
def exit_quote(body: TicketBody, request: Request, response: Response,
               session: Session = Depends(get_session),
               staff: Staff = Depends(require_roles(*SALIDA_ROLES))):
    payload = quote_stay(session, request.app.state.clock.now(), body.ticket_code)
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
            request=request, name="exits/unauthorized.html", status_code=401,
            context={"staff": None}))
    if staff.role not in SALIDA_ROLES:
        return _no_store(templates.TemplateResponse(
            request=request, name="exits/forbidden.html", status_code=403,
            context={"staff": staff}))
    return None


def _salidas_page(request: Request, staff: Staff, *, quote=None, error=None,
                  status: int = 200, code: str = ""):
    now = request.app.state.clock.now()
    context = {"staff": staff, "as_of": local_time(now), "quote": quote,
               "error": error, "code": code}
    if quote is not None:
        context["entered"] = local_time(quote["entered_at"])
    return _no_store(templates.TemplateResponse(
        request=request, name="exits/salidas.html", status_code=status,
        context=context))


@views.get("/salidas", response_class=HTMLResponse)
def salidas_page(request: Request, session: Session = Depends(get_session)):
    staff = _optional_staff(request, session)
    denied = _denied(request, staff)
    if denied is not None:
        return denied
    return _salidas_page(request, staff)


@views.post("/salidas/cotizar", response_class=HTMLResponse,
            dependencies=[Depends(same_origin)])
def salidas_quote(request: Request, ticket_code: str = Form(default=""),
                  session: Session = Depends(get_session)):
    staff = _optional_staff(request, session)
    denied = _denied(request, staff)
    if denied is not None:
        return denied
    now = request.app.state.clock.now()
    try:
        payload = quote_stay(session, now, ticket_code)
    except AppError as exc:
        if exc.status not in {404, 409, 422}:
            raise
        return _salidas_page(request, staff, error=exc.message, status=exc.status,
                             code=ticket_code)
    return _salidas_page(request, staff, quote=payload, code=ticket_code)
