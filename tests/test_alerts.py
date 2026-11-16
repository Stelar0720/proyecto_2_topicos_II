"""HU-05 T-05A - alertas de estadias >24h (AC-12/13)."""
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from plaza_reserva.cli import create_staff, seed_spaces
from plaza_reserva.models import Allocation, Stay
from plaza_reserva.security import new_token, token_digest

ORIGIN = {"Origin": "http://testserver"}
PASSWORD = "solo-para-prueba-aleatoria"


def seed(engine):
    with Session(engine) as session:
        seed_spaces(session)


def login(client, engine, clock, username, role):
    with Session(engine) as session:
        create_staff(session, username, role, PASSWORD, clock)
    response = client.post("/api/auth/login",
                           json={"username": username, "password": PASSWORD}, headers=ORIGIN)
    assert response.status_code == 200, response.text


def make_open_stay(engine, plate, space, entered_at):
    with Session(engine) as session:
        stay = Stay(plate=plate, space_id=space, ticket_hash=token_digest(new_token()),
                    status="open", entered_at=entered_at)
        session.add(stay)
        session.flush()
        session.add(Allocation(space_id=space, plate=plate, stay_id=stay.id))
        session.commit()
        return stay.id


def make_closed_stay(engine, plate, space, entered_at, exited_at):
    with Session(engine) as session:
        stay = Stay(plate=plate, space_id=space, ticket_hash=token_digest(new_token()),
                    status="closed", entered_at=entered_at, exited_at=exited_at)
        session.add(stay)
        session.commit()
        return stay.id


def alerts(client):
    return client.get("/api/alerts/long-stays")


def test_alert_boundaries_strictly_over_24h(client, engine, clock):
    seed(engine)
    login(client, engine, clock, "vigia1", "vigilancia")
    base = clock.value
    make_open_stay(engine, "B2401", "G001", base - timedelta(hours=24, seconds=-1))  # 23:59:59
    make_open_stay(engine, "B2402", "G002", base - timedelta(hours=24))              # exact 24h
    make_open_stay(engine, "B2403", "G003", base - timedelta(hours=24, seconds=1))   # 24h+1s
    resp = alerts(client)
    assert resp.status_code == 200
    data = resp.json()
    plates = [i["plate"] for i in data["items"]]
    assert plates == ["B2403"]
    assert data["items"][0]["space_code"] == "G003"
    assert data["items"][0]["elapsed_seconds"] == 24 * 3600 + 1
    assert data["as_of"] is not None


def test_alert_excludes_closed_stays(client, engine, clock):
    seed(engine)
    login(client, engine, clock, "vigia2", "vigilancia")
    base = clock.value
    make_open_stay(engine, "OPEN25", "G001", base - timedelta(hours=25))
    make_closed_stay(engine, "CLSD30", "G002", base - timedelta(hours=30), base - timedelta(hours=1))
    data = alerts(client).json()
    plates = [i["plate"] for i in data["items"]]
    assert "OPEN25" in plates and "CLSD30" not in plates


def test_alert_requires_staff_and_allowed_roles(client, engine, clock):
    seed(engine)
    assert alerts(client).status_code == 401
    # vigilancia permitido
    login(client, engine, clock, "vigia3", "vigilancia")
    assert alerts(client).status_code == 200
    # celador permitido
    login(client, engine, clock, "cel1", "celador")
    assert alerts(client).status_code == 200
    # admin permitido
    login(client, engine, clock, "adm1", "admin")
    assert alerts(client).status_code == 200


def test_alert_view_access_and_content(client, engine, clock):
    seed(engine)
    page = client.get("/vigilancia")
    assert page.status_code == 401
    login(client, engine, clock, "vigia4", "vigilancia")
    base = clock.value
    make_open_stay(engine, "ALRV1", "G001", base - timedelta(hours=25))
    page = client.get("/vigilancia")
    assert page.status_code == 200
    assert "ALRV1" in page.text and "G001" in page.text
    assert "informativa" in page.text.lower()
