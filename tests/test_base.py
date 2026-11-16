from datetime import timedelta

from sqlalchemy import func, inspect, select
from sqlalchemy.orm import Session

from plaza_reserva.cli import create_staff, seed_spaces
from plaza_reserva.models import AllocationGuard, Space, StaffSession
from plaza_reserva.security import token_digest

ORIGIN = {"Origin": "http://testserver"}
PASSWORD = "solo-para-prueba-aleatoria"


def test_health_and_pending_navigation(client):
    assert client.get("/health").json() == {"status": "ok", "database": "ok"}
    page = client.get("/")
    assert page.status_code == 200
    assert "Base inicial" in page.text
    assert "pendientes" in page.text
    assert client.post("/api/reservations", json={"plate": "ABC123"}).status_code == 404


def test_seed_idempotent_preserves_existing(engine, clock):
    with Session(engine) as session:
        create_staff(session, "operador", "celador", PASSWORD, clock)
        assert seed_spaces(session) == 100
        assert seed_spaces(session) == 0
        rows = session.scalars(select(Space)).all()
        assert {s.code for s in rows} == ({f"P{i:03}" for i in range(1, 21)} |
                                        {f"G{i:03}" for i in range(1, 81)})
        assert sum(s.category == "preferential" for s in rows) == 20
        assert client_staff_exists(session)


def client_staff_exists(session):
    from plaza_reserva.models import Staff
    return session.scalar(select(Staff).where(Staff.username == "operador")) is not None


def test_unauthorized(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/personal").status_code == 401


def test_login_expiry_and_revocation(client, engine, clock):
    with Session(engine) as session:
        create_staff(session, "celador1", "celador", PASSWORD, clock)
    credentials = {"username": "celador1", "password": PASSWORD}
    login = client.post("/api/auth/login", json=credentials, headers=ORIGIN)
    assert login.status_code == 200
    assert "HttpOnly" in login.headers["set-cookie"]
    assert "SameSite=strict" in login.headers["set-cookie"]
    raw = client.cookies.get("plaza_session")
    with Session(engine) as session:
        assert session.get(StaffSession, raw) is None
        assert session.get(StaffSession, token_digest(raw)) is not None
    assert client.get("/api/auth/me").json()["role"] == "celador"
    assert client.get("/personal").status_code == 200
    # Exactamente al límite ya no autoriza.
    clock.value += timedelta(hours=8)
    assert client.get("/api/auth/me").status_code == 401
    assert client.post("/api/auth/login", json=credentials, headers=ORIGIN).status_code == 200
    assert client.post("/api/auth/logout", headers=ORIGIN).status_code == 204
    assert client.post("/api/auth/logout", headers=ORIGIN).status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_origin_and_invalid_credentials(client):
    body = {"username": "nadie", "password": PASSWORD}
    assert client.post("/api/auth/login", json=body).status_code == 403
    assert client.post("/api/auth/login", json=body, headers={"Origin": "https://ajeno.invalid"}).status_code == 403
    invalid = client.post("/api/auth/login", json=body, headers=ORIGIN)
    assert invalid.status_code == 401
    assert PASSWORD not in invalid.text
    invalid = client.post("/api/auth/login", json={"username": "x", "password": "secreto"}, headers=ORIGIN)
    assert invalid.status_code == 422
    assert "secreto" not in invalid.text


def test_migration_creates_guard_and_tables(engine):
    assert {"spaces", "staff", "staff_sessions", "reservations", "stays", "allocations", "payments"} <= set(inspect(engine).get_table_names())
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(AllocationGuard)) == 1
