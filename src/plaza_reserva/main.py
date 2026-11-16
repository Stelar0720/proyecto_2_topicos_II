from contextlib import asynccontextmanager
from datetime import timedelta
from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .auth import LoginLimiter, current_staff, router
from .clock import SystemClock
from .config import Settings
from .db import build_engine
from .models import Reservation, Space, Stay
from .entries import router as entries_router, views as entries_views
from .errors import AppError
from .exits import router as exits_router, views as exits_views
from .alerts import router as alerts_router, views as alerts_views
from .reservations import router as reservations_router, views as reservations_views
from .reservations import local_time, qr_svg
from .security import hash_password, new_token

ROOT = Path(__file__).parent


def create_app(settings=None, clock=None, engine=None):
    settings = settings or Settings.from_env()
    owns_engine = engine is None
    engine = engine or build_engine(settings.database_url)

    @asynccontextmanager
    async def lifespan(app):
        yield
        if owns_engine:
            engine.dispose()

    app = FastAPI(title="Plaza Reserva — base inicial", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.clock = clock or SystemClock()
    app.state.engine = engine
    app.state.login_limiter = LoginLimiter()
    app.state.dummy_password_hash = hash_password(new_token())
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts))
    templates = Jinja2Templates(directory=str(ROOT / "templates"))
    app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
    app.include_router(router)
    app.include_router(reservations_router)
    app.include_router(reservations_views)
    app.include_router(entries_router)
    app.include_router(entries_views)
    app.include_router(exits_router)
    app.include_router(exits_views)
    app.include_router(alerts_router)
    app.include_router(alerts_views)

    def error_response(status, code, message):
        return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}},
                            headers={"Cache-Control": "no-store"})

    @app.exception_handler(AppError)
    async def app_error(request, exc):
        if request.url.path == "/personal" and exc.status == 401:
            return templates.TemplateResponse(request=request, name="unauthorized.html", status_code=401)
        return error_response(exc.status, exc.code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def invalid(request, exc):
        return error_response(422, "VALIDATION_ERROR", "Datos inválidos; revisa los campos")

    @app.exception_handler(HTTPException)
    async def http_error(request, exc):
        return error_response(exc.status_code, "NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR",
                              "Recurso no encontrado" if exc.status_code == 404 else "Petición rechazada")

    @app.exception_handler(SQLAlchemyError)
    async def database_error(request, exc):
        return error_response(503, "DATABASE_UNAVAILABLE", "Datos temporalmente no disponibles")

    @app.middleware("http")
    async def headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        if request.url.path == "/personal" or request.url.path.startswith("/api/auth"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/health")
    def health():
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request):
        return templates.TemplateResponse(request=request, name="home.html")

    @app.get("/acceso", response_class=HTMLResponse)
    def access(request: Request):
        return templates.TemplateResponse(request=request, name="login.html")

    @app.get("/personal", response_class=HTMLResponse)
    def staff_home(request: Request, staff=Depends(current_staff)):
        if staff.role != "admin":
            raise AppError(403, "FORBIDDEN", "Área exclusiva de administración")
        now = request.app.state.clock.now()
        with engine.connect() as connection:
            spaces = connection.execute(text("SELECT code FROM spaces ORDER BY code")).scalars().all()
        with Session(engine) as session:
            open_stays = {s.space_id: s for s in session.query(Stay).filter(Stay.status == "open")}
            active_reservations = session.query(Reservation).filter(
                Reservation.status == "pending", Reservation.scheduled_at <= now,
                Reservation.expires_at > now).all()
            reserved = {reservation.space_id for reservation in active_reservations}
            reservation_by_space = {reservation.space_id: reservation for reservation in active_reservations}
            reservation_by_id = {reservation.id: reservation for reservation in session.query(Reservation).all()}
        cards = []
        for code in spaces:
            stay = open_stays.get(code)
            reservation = reservation_by_id.get(stay.reservation_id) if stay and stay.reservation_id else reservation_by_space.get(code)
            state = "alert" if stay and now - stay.entered_at > timedelta(hours=24) else "occupied" if stay or code in reserved else "available"
            detail = None
            if state == "occupied":
                detail = {
                    "kind": "Vehículo ingresado" if stay else "Reserva activa",
                    "customer_name": reservation.customer_name if reservation else "Ingreso sin reserva",
                    "plate": stay.plate if stay else reservation.plate,
                    "scheduled": local_time(reservation.scheduled_at or reservation.created_at) if reservation else None,
                    "entered": local_time(stay.entered_at) if stay else None,
                    "code": stay.access_code if stay else reservation.access_code,
                }
            cards.append({"code": code, "state": state, "detail": detail})
        return templates.TemplateResponse(request=request, name="staff.html", context={
            "staff": staff, "rows": [cards[i:i+10] for i in range(0, len(cards), 10)], "qr_svg": qr_svg})

    @app.get("/api/dashboard/spaces")
    def dashboard_spaces(request: Request, staff=Depends(current_staff)):
        if staff.role != "admin":
            raise AppError(403, "FORBIDDEN", "Área exclusiva de administración")
        now = request.app.state.clock.now()
        with Session(engine) as session:
            open_stays = {s.space_id: s for s in session.query(Stay).filter(Stay.status == "open")}
            reserved = {r.space_id for r in session.query(Reservation).filter(
                Reservation.status == "pending", Reservation.scheduled_at <= now,
                Reservation.expires_at > now)}
        with engine.connect() as connection:
            spaces = connection.execute(text("SELECT code FROM spaces ORDER BY code")).scalars().all()
        return {"as_of": now, "spaces": [{"code": code, "state": (
            "alert" if code in open_stays and now - open_stays[code].entered_at > timedelta(hours=24)
            else "occupied" if code in open_stays or code in reserved else "available"
        )} for code in spaces]}

    @app.get("/cliente", response_class=HTMLResponse)
    def client_home(request: Request, staff=Depends(current_staff)):
        if staff.role != "client":
            raise AppError(403, "FORBIDDEN", "Área exclusiva de clientes")
        return templates.TemplateResponse(request=request, name="client.html", context={"staff": staff})

    return app
