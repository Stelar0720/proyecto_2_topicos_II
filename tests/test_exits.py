"""HU-04 T-04A - cotizacion de salida (AC-09/13). No muta la estadia."""
import re
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from plaza_reserva.cli import create_staff, seed_spaces
from plaza_reserva.models import Allocation, Payment, Stay
from plaza_reserva.security import token_digest

ORIGIN = {"Origin": "http://testserver"}
PASSWORD = "solo-para-prueba-aleatoria"


def seed(engine):
    with Session(engine) as session:
        seed_spaces(session)


def login(client, engine, clock, username="celador1", role="celador"):
    with Session(engine) as session:
        create_staff(session, username, role, PASSWORD, clock)
    response = client.post("/api/auth/login",
                           json={"username": username, "password": PASSWORD}, headers=ORIGIN)
    assert response.status_code == 200, response.text


def walk_in(client, plate):
    response = client.post("/api/entries/walk-in", json={"plate": plate}, headers=ORIGIN)
    assert response.status_code == 201, response.text
    return response.json()


def quote(client, ticket_code):
    return client.post("/api/exits/quote", json={"ticket_code": ticket_code}, headers=ORIGIN)


def snapshot(engine):
    with Session(engine) as session:
        stay = session.scalar(select(Stay))
        return (stay.status, stay.exited_at,
                session.scalar(select(func.count()).select_from(Payment)),
                session.scalar(select(func.count()).select_from(Allocation)),
                session.get(Allocation, stay.space_id).stay_id)


def test_quote_amounts_ac09_boundaries(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    ticket = walk_in(client, "EXIT01")["ticket_code"]
    base = clock.value
    cases = [
        (timedelta(seconds=0), 0),
        (timedelta(seconds=1), 2),
        (timedelta(seconds=60), 2),
        (timedelta(seconds=60, microseconds=1), 4),
        (timedelta(seconds=3900), 130),
    ]
    for delta, cents in cases:
        clock.value = base + delta
        response = quote(client, ticket)
        assert response.status_code == 200, (delta, response.text)
        body = response.json()
        assert body["amount_cents"] == cents
        assert body["plate"] == "EXIT01" and body["space_code"] == "G001"
        assert body["status"] == "open"


def test_quote_does_not_mutate_stay(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    ticket = walk_in(client, "EXIT02")["ticket_code"]
    before = snapshot(engine)
    clock.value += timedelta(minutes=10)
    response = quote(client, ticket)
    assert response.status_code == 200 and response.json()["amount_cents"] == 20
    assert snapshot(engine) == before


def test_quote_unknown_ticket_is_generic(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    response = quote(client, "codigo-inventado")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert "EXIT" not in response.text


def test_quote_requires_staff_and_role(client, engine, clock):
    seed(engine)
    ticket = walk_in_as_celador = None
    login(client, engine, clock)
    ticket = walk_in(client, "EXIT03")["ticket_code"]
    # nueva sesion: logout implicito creando otro cliente no es necesario; probamos sin cookie
    from fastapi.testclient import TestClient
    settings = client.app.state.settings
    with TestClient(client.app) as anon:
        unauth = anon.post("/api/exits/quote", json={"ticket_code": ticket}, headers=ORIGIN)
        assert unauth.status_code == 401
    login(client, engine, clock, username="vigia1", role="vigilancia")
    forbidden = quote(client, ticket)
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "FORBIDDEN"


def test_quote_requires_same_origin(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    ticket = walk_in(client, "EXIT04")["ticket_code"]
    response = client.post("/api/exits/quote", json={"ticket_code": ticket})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ORIGIN_REQUIRED"


def test_salidas_view_quote_flow(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    ticket = walk_in(client, "EXIT05")["ticket_code"]
    clock.value += timedelta(minutes=65)
    page = client.post("/salidas/cotizar", data={"ticket_code": ticket}, headers=ORIGIN)
    assert page.status_code == 200
    assert "EXIT05" in page.text and "G001" in page.text
    assert "130" in page.text
    assert page.headers["cache-control"] == "no-store"
    assert snapshot(engine)[0] == "open"


def test_salidas_view_access_control(client, engine, clock):
    seed(engine)
    page = client.get("/salidas")
    assert page.status_code == 401
    login(client, engine, clock, username="vigia2", role="vigilancia")
    page = client.get("/salidas")
    assert page.status_code == 403
