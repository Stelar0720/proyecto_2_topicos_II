from datetime import timedelta
from threading import Lock

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, Field, SecretStr
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import get_session
from .errors import AppError
from .models import Staff, StaffSession
from .security import new_token, token_digest, verify_password

router = APIRouter(prefix="/api/auth", tags=["personal"])
COOKIE = "plaza_session"


class LoginBody(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: SecretStr = Field(min_length=12, max_length=128)


class LoginLimiter:
    """Fundamento local; antes de multiworker sustituir por limitador compartido."""
    def __init__(self):
        self._attempts = {}
        self._lock = Lock()

    def check(self, key, now):
        with self._lock:
            self._attempts = {k: v for k, v in self._attempts.items() if v[1] > now}
            count, until = self._attempts.get(key, (0, now + timedelta(minutes=1)))
            if count >= 5:
                raise AppError(429, "RATE_LIMITED", "Espera un minuto antes de reintentar")
            self._attempts[key] = (count + 1, until)


def same_origin(request: Request):
    if request.headers.get("origin") != str(request.base_url).rstrip("/"):
        raise AppError(403, "ORIGIN_REQUIRED", "Se requiere el mismo origen")


def staff_dict(staff: Staff):
    return {"id": staff.id, "username": staff.username, "role": staff.role}


def current_staff(request: Request, session: Session = Depends(get_session)):
    raw = request.cookies.get(COOKIE)
    if not raw or len(raw) > 128:
        raise AppError(401, "AUTH_REQUIRED", "Inicia sesión como personal")
    stored = session.get(StaffSession, token_digest(raw))
    now = request.app.state.clock.now()
    if stored is None or stored.expires_at <= now:
        raise AppError(401, "AUTH_REQUIRED", "Sesión inválida o vencida")
    staff = session.get(Staff, stored.staff_id)
    if staff is None or not staff.active:
        raise AppError(401, "AUTH_REQUIRED", "Sesión inválida o vencida")
    return staff


def require_roles(*roles):
    def dependency(staff: Staff = Depends(current_staff)):
        if staff.role not in roles:
            raise AppError(403, "FORBIDDEN", "Operación no autorizada")
        return staff
    return dependency


@router.post("/login", dependencies=[Depends(same_origin)])
def login(body: LoginBody, request: Request, response: Response,
          session: Session = Depends(get_session)):
    now = request.app.state.clock.now()
    request.app.state.login_limiter.check(request.client.host if request.client else "unknown", now)
    username = body.username.strip().lower()
    staff = session.scalar(select(Staff).where(Staff.username == username))
    encoded = staff.password_hash if staff else request.app.state.dummy_password_hash
    valid = verify_password(body.password.get_secret_value(), encoded)
    if not valid or staff is None or not staff.active:
        raise AppError(401, "INVALID_CREDENTIALS", "Credenciales inválidas")
    # Rotación: revocar cookie anterior si existe, sin imprimir su valor.
    old = request.cookies.get(COOKIE)
    if old and len(old) <= 128:
        previous = session.get(StaffSession, token_digest(old))
        if previous:
            session.delete(previous)
    raw = new_token()
    session.add(StaffSession(token_hash=token_digest(raw), staff_id=staff.id,
                             created_at=now, expires_at=now + timedelta(
                                 hours=request.app.state.settings.session_hours)))
    session.commit()
    response.set_cookie(COOKIE, raw, max_age=request.app.state.settings.session_hours * 3600,
                        httponly=True, secure=request.app.state.settings.cookie_secure,
                        samesite="strict", path="/")
    response.headers["Cache-Control"] = "no-store"
    return staff_dict(staff)


@router.get("/me")
def me(response: Response, staff: Staff = Depends(current_staff)):
    response.headers["Cache-Control"] = "no-store"
    return staff_dict(staff)


@router.post("/logout", status_code=204, dependencies=[Depends(same_origin)])
def logout(request: Request, session: Session = Depends(get_session)):
    raw = request.cookies.get(COOKIE)
    if raw and len(raw) <= 128:
        stored = session.get(StaffSession, token_digest(raw))
        if stored:
            session.delete(stored)
            session.commit()
    response = Response(status_code=204)
    response.delete_cookie(COOKIE, path="/", secure=request.app.state.settings.cookie_secure,
                           httponly=True, samesite="strict")
    return response
