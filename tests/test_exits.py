"""HU-04 T-04A/B - cotizacion y cierre idempotente (AC-09/10/11/13)."""
import threading
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from plaza_reserva.cli import create_staff, seed_spaces
from plaza_reserva.errors import AppError
from plaza_reserva.exits import close_stay
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


def close(client, ticket_code, key, confirmed=True):
    headers = {**ORIGIN, "Idempotency-Key": key}
    return client.post("/api/exits/close",
                       json={"ticket_code": ticket_code, "payment_confirmed": confirmed},
                       headers=headers)


def db_state(engine, space="G001"):
    with Session(engine) as session:
        stay = session.scalar(select(Stay))
        payment = session.scalar(select(Payment))
        alloc = session.get(Allocation, space)
        return stay, payment, alloc


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
    with Session(engine) as session:
        before = (session.scalar(select(Stay)).status,
                  session.scalar(select(func.count()).select_from(Payment)),
                  session.scalar(select(func.count()).select_from(Allocation)))
    clock.value += timedelta(minutes=10)
    response = quote(client, ticket)
    assert response.status_code == 200 and response.json()["amount_cents"] == 20
    with Session(engine) as session:
        after = (session.scalar(select(Stay)).status,
                 session.scalar(select(func.count()).select_from(Payment)),
                 session.scalar(select(func.count()).select_from(Allocation)))
    assert before == after


def test_quote_unknown_ticket_is_generic(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    response = quote(client, "codigo-inventado")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_quote_requires_staff_role_and_origin(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    ticket = walk_in(client, "EXIT03")["ticket_code"]
    from fastapi.testclient import TestClient
    with TestClient(client.app) as anon:
        unauth = anon.post("/api/exits/quote", json={"ticket_code": ticket}, headers=ORIGIN)
        assert unauth.status_code == 401
    login(client, engine, clock, username="vigia1", role="vigilancia")
    assert quote(client, ticket).status_code == 403
    login(client, engine, clock, username="celador1b", role="celador")
    assert client.post("/api/exits/quote", json={"ticket_code": ticket}).status_code == 403


def test_close_records_payment_closes_and_frees_space(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    ticket = walk_in(client, "EXIT10")["ticket_code"]
    clock.value += timedelta(minutes=65)
    response = close(client, ticket, "key-close-1")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["amount_cents"] == 130
    assert body["status"] == "closed"
    assert body["exited_at"] is not None and body["paid_at"] == body["exited_at"]
    stay, payment, alloc = db_state(engine)
    assert stay.status == "closed" and stay.exited_at == clock.value
    assert payment.amount_cents == 130 and payment.idempotency_key == "key-close-1"
    assert alloc is None
    assert client.get("/api/availability").json()["general"]["available"] == 80


def test_close_retry_same_key_returns_original(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    ticket = walk_in(client, "EXIT11")["ticket_code"]
    clock.value += timedelta(minutes=10)
    first = close(client, ticket, "key-retry-1").json()
    clock.value += timedelta(minutes=30)
    second = close(client, ticket, "key-retry-1").json()
    assert first["exited_at"] == second["exited_at"]
    assert first["amount_cents"] == second["amount_cents"] == 20
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(Payment)) == 1


def test_close_key_reused_for_other_ticket_conflicts(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    t1 = walk_in(client, "EXIT12")["ticket_code"]
    t2 = walk_in(client, "EXIT13")["ticket_code"]
    clock.value += timedelta(minutes=5)
    assert close(client, t1, "shared-key").status_code == 200
    resp = close(client, t2, "shared-key")
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "IDEMPOTENCY_CONFLICT"
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(Payment)) == 1
        stay2 = session.scalar(select(Stay).where(Stay.plate == "EXIT13"))
        assert stay2.status == "open"


def test_closed_ticket_reused_on_new_occupant_does_not_affect_new_stay(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    t1 = walk_in(client, "EXIT14")["ticket_code"]
    clock.value += timedelta(minutes=5)
    assert close(client, t1, "k-old").status_code == 200
    t2 = walk_in(client, "EXIT14B")["ticket_code"]
    clock.value += timedelta(minutes=5)
    # intentar cerrar el ticket ya cerrado (otro intento, otra clave) -> devuelve cierre original, no toca nuevo
    resp = close(client, t1, "k-old-2")
    assert resp.status_code == 200
    assert resp.json()["plate"] == "EXIT14"
    with Session(engine) as session:
        stay_new = session.scalar(select(Stay).where(Stay.plate == "EXIT14B"))
        stay_old = session.scalar(select(Stay).where(Stay.plate == "EXIT14"))
        assert stay_new.status == "open"
        assert session.get(Allocation, stay_new.space_id).stay_id == stay_new.id
        assert session.scalar(select(func.count()).select_from(Payment)) == 1


def test_concurrent_close_same_ticket_single_payment(engine, clock):
    seed(engine)
    # preparar staff y estadia via API-like directo
    with Session(engine) as session:
        create_staff(session, "celadorc", "celador", PASSWORD, clock)
        from plaza_reserva.entries import enter_walk_in
        entry = enter_walk_in(session, clock.value, "RACE20")
        ticket = entry["ticket_code"]
        staff_id = session.scalar(select(__import__('plaza_reserva.models', fromlist=['Staff']).Staff.id))
    clock.value += timedelta(minutes=10)
    results = []
    barrier = threading.Barrier(2)

    def worker(key):
        barrier.wait()
        try:
            with Session(engine) as session:
                sid = session.scalar(select(__import__('plaza_reserva.models', fromlist=['Staff']).Staff.id))
            with Session(engine) as session:
                results.append(("ok", close_stay(session, clock.value, ticket, sid, key)))
        except AppError as exc:
            results.append(("error", exc.code))

    threads = [threading.Thread(target=worker, args=(k,)) for k in ("race-k1", "race-k2")]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=20)
    assert not any(t.is_alive() for t in threads)
    oks = [r for r in results if r[0] == "ok"]
    assert len(oks) >= 1
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(Payment)) == 1
        stay = session.scalar(select(Stay))
        assert stay.status == "closed"
        assert session.get(Allocation, stay.space_id) is None


def test_close_requires_confirmation_origin_and_role(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    ticket = walk_in(client, "EXIT30")["ticket_code"]
    # sin confirmacion
    resp = client.post("/api/exits/close", json={"ticket_code": ticket, "payment_confirmed": False},
                       headers={**ORIGIN, "Idempotency-Key": "k"})
    assert resp.status_code == 422
    # sin origin
    resp = client.post("/api/exits/close", json={"ticket_code": ticket, "payment_confirmed": True},
                       headers={"Idempotency-Key": "k"})
    assert resp.status_code == 403
    # rol
    login(client, engine, clock, username="vigia3", role="vigilancia")
    resp = close(client, ticket, "k2")
    assert resp.status_code == 403


def test_salidas_view_close_flow(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    ticket = walk_in(client, "EXIT40")["ticket_code"]
    clock.value += timedelta(minutes=5)
    page = client.post("/salidas/cerrar",
                       data={"ticket_code": ticket, "payment_confirmed": "on", "idempotency_key": "form-k1"},
                       headers=ORIGIN)
    assert page.status_code == 200
    assert "EXIT40" in page.text
    assert "Cierre registrado" in page.text
    stay, payment, alloc = db_state(engine)
    assert stay.status == "closed" and payment is not None and alloc is None
