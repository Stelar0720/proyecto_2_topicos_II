"""HU-03 · AC-05/06/07/08/13 sobre ingreso con reserva y espontáneo."""
import re
import threading
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from plaza_reserva.cli import create_staff, seed_spaces
from plaza_reserva.entries import enter_walk_in
from plaza_reserva.errors import AppError
from plaza_reserva.models import Allocation, Reservation, Stay
from plaza_reserva.security import new_token, token_digest

ORIGIN = {"Origin": "http://testserver"}
PASSWORD = "solo-para-prueba-aleatoria"
CODE_PATTERN = re.compile(r"<code>([A-Za-z0-9_-]{43})</code>")


def seed(engine):
    with Session(engine) as session:
        seed_spaces(session)


def login(client, engine, clock, username="celador1", role="celador"):
    with Session(engine) as session:
        create_staff(session, username, role, PASSWORD, clock)
    response = client.post("/api/auth/login",
                           json={"username": username, "password": PASSWORD}, headers=ORIGIN)
    assert response.status_code == 200, response.text


def reserve(client, plate):
    response = client.post("/api/reservations", json={"plate": plate}, headers=ORIGIN)
    assert response.status_code == 201, response.text
    return response.json()


def entry_reservation(client, code, plate):
    return client.post("/api/entries/reservation",
                       json={"private_code": code, "plate": plate}, headers=ORIGIN)


def walk_in(client, plate):
    return client.post("/api/entries/walk-in", json={"plate": plate}, headers=ORIGIN)


def fill_general(engine, clock, total):
    with Session(engine) as session:
        for index in range(1, total + 1):
            code = f"G{index:03}"
            plate = f"WALK{index:03}"
            stay = Stay(plate=plate, space_id=code, ticket_hash=token_digest(new_token()),
                        status="open", entered_at=clock.value)
            session.add(stay)
            session.flush()
            session.add(Allocation(space_id=code, plate=plate, stay_id=stay.id))
        session.commit()


def counts(engine):
    with Session(engine) as session:
        return (session.scalar(select(func.count()).select_from(Stay)),
                session.scalar(select(func.count()).select_from(Allocation)))


def session_stays(engine):
    with Session(engine) as session:
        return session.scalar(select(func.count()).select_from(Stay))


def test_entry_with_reservation_converts_atomically(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    reservation = reserve(client, "ENTR01")
    response = entry_reservation(client, reservation["private_code"], "ENTR01")
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["space_code"] == "P001"
    assert body["status"] == "open"
    assert body["plate"] == "ENTR01"
    with Session(engine) as session:
        stay = session.scalar(select(Stay))
        stored = session.scalar(select(Reservation))
        allocation = session.get(Allocation, "P001")
        assert stay.status == "open" and stay.reservation_id == stored.id
        assert stored.status == "used" and stored.used_at == clock.value
        assert allocation.reservation_id is None
        assert allocation.stay_id == stay.id
        assert stay.ticket_hash == token_digest(body["ticket_code"])
        assert stay.ticket_hash != body["ticket_code"]
    availability = client.get("/api/availability").json()
    assert availability["preferential"]["available"] == 19
    assert availability["general"]["available"] == 80


def test_entry_wrong_plate_is_rejected_without_writes(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    reservation = reserve(client, "ENTR02")
    response = entry_reservation(client, reservation["private_code"], "OTRA02")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PLATE_MISMATCH"
    assert counts(engine) == (0, 1)
    with Session(engine) as session:
        assert session.scalar(select(Reservation.status)) == "pending"


def test_entry_expired_reservation_is_rejected_and_releases_space(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    reservation = reserve(client, "ENTR03")
    clock.value += timedelta(minutes=31)
    response = entry_reservation(client, reservation["private_code"], "ENTR03")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "RESERVATION_EXPIRED"
    # El rechazo revierte la normalización; la lectura ya no cuenta la reserva vencida
    # y la siguiente asignación limpia la fila obsoleta dentro del bloqueo.
    assert counts(engine) == (0, 1)
    assert client.get("/api/availability").json()["preferential"]["available"] == 20
    assert reserve(client, "ENTR03")["space_code"] == "P001"
    with Session(engine) as session:
        assert sorted(session.scalars(select(Reservation.status)).all()) == ["expired", "pending"]
    assert counts(engine) == (0, 1)


def test_entry_cancelled_reservation_is_rejected(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    reservation = reserve(client, "ENTR04")
    client.post("/api/reservations/cancel",
                json={"private_code": reservation["private_code"]}, headers=ORIGIN)
    response = entry_reservation(client, reservation["private_code"], "ENTR04")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "RESERVATION_CANCELLED"


def test_entry_is_used_only_once(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    reservation = reserve(client, "ENTR05")
    assert entry_reservation(client, reservation["private_code"], "ENTR05").status_code == 201
    again = entry_reservation(client, reservation["private_code"], "ENTR05")
    assert again.status_code == 409
    assert again.json()["error"]["code"] == "RESERVATION_USED"
    assert counts(engine) == (1, 1)


def test_entry_with_unknown_code_is_generic(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    response = entry_reservation(client, "codigo-inventado", "ENTR06")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert counts(engine) == (0, 0)


def test_walk_in_assigns_general_and_never_preferential(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    response = walk_in(client, "walk-01")
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["space_code"] == "G001"
    assert body["plate"] == "WALK-01"
    with Session(engine) as session:
        stay = session.scalar(select(Stay))
        allocation = session.get(Allocation, "G001")
        assert stay.reservation_id is None
        assert allocation.stay_id == stay.id
        assert stay.ticket_hash == token_digest(body["ticket_code"])
    availability = client.get("/api/availability").json()
    assert availability["general"]["available"] == 79
    assert availability["preferential"]["available"] == 20


def test_walk_in_rejects_plate_with_pending_reservation(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    reserve(client, "ENTR07")
    response = walk_in(client, "ENTR07")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PLATE_BUSY"
    assert counts(engine) == (0, 1)


def test_walk_in_rejects_plate_with_open_stay(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    assert walk_in(client, "ENTR08").status_code == 201
    response = walk_in(client, "ENTR08")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PLATE_BUSY"
    assert counts(engine) == (1, 1)


def test_full_general_category_rejects_without_partial_rows(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    fill_general(engine, clock, 80)
    response = walk_in(client, "FULL01")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CATEGORY_FULL"
    assert counts(engine) == (80, 80)


def test_simultaneous_walk_ins_for_last_general_single_winner(engine, clock):
    seed(engine)
    fill_general(engine, clock, 79)
    barrier = threading.Barrier(2)
    results = []

    def worker(plate):
        barrier.wait()
        try:
            with Session(engine) as session:
                results.append(("ok", enter_walk_in(session, clock.value, plate)["space_code"]))
        except AppError as exc:
            results.append(("error", exc.code))

    threads = [threading.Thread(target=worker, args=(plate,)) for plate in ("RACE01", "RACE02")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=20)
    assert not any(thread.is_alive() for thread in threads)
    assert sorted(result[0] for result in results) == ["error", "ok"]
    assert [result[1] for result in results if result[0] == "error"] == ["CATEGORY_FULL"]
    assert counts(engine) == (80, 80)


def test_entry_endpoints_require_staff_and_role(client, engine, clock):
    seed(engine)
    reservation = reserve(client, "ENTR09")
    unauthenticated = entry_reservation(client, reservation["private_code"], "ENTR09")
    assert unauthenticated.status_code == 401
    login(client, engine, clock, username="vigia1", role="vigilancia")
    forbidden = walk_in(client, "ENTR09")
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "FORBIDDEN"
    assert counts(engine) == (0, 1)


def test_entry_mutations_require_same_origin(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    response = client.post("/api/entries/walk-in", json={"plate": "ORIG09"})
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "ORIGIN_REQUIRED"
    assert counts(engine) == (0, 0)


def test_garita_view_requires_staff_role(client, engine, clock):
    seed(engine)
    page = client.get("/garita")
    assert page.status_code == 401
    assert "Iniciar sesión" in page.text or "iniciar sesión" in page.text
    assert 'href="/acceso"' in page.text
    login(client, engine, clock, username="vigia2", role="vigilancia")
    page = client.get("/garita")
    assert page.status_code == 403
    assert "no registra ingresos" in page.text


def test_garita_form_issues_printable_ticket(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    page = client.get("/garita")
    assert page.status_code == 200
    assert 'action="/garita/reserva"' in page.text
    assert 'action="/garita/espontaneo"' in page.text
    ticket = client.post("/garita/espontaneo", data={"plate": "TICK09"}, headers=ORIGIN)
    assert ticket.status_code == 200
    assert ticket.headers["cache-control"] == "no-store"
    assert "G001" in ticket.text and "TICK09" in ticket.text
    assert "print-ticket" in ticket.text
    match = CODE_PATTERN.search(ticket.text)
    assert match, ticket.text
    svg = re.search(r"<svg.*?</svg>", ticket.text, re.S).group(0)
    assert "TICK09" not in svg
    with Session(engine) as session:
        assert session.scalar(select(Stay.ticket_hash)) == token_digest(match.group(1))


def test_garita_form_reports_reservation_conflict(client, engine, clock):
    seed(engine)
    login(client, engine, clock)
    reservation = reserve(client, "ENTR10")
    clock.value += timedelta(minutes=31)
    page = client.post("/garita/reserva",
                       data={"private_code": reservation["private_code"], "plate": "ENTR10"},
                       headers=ORIGIN)
    assert page.status_code == 409
    assert "No se registró el ingreso" in page.text
    assert session_stays(engine) == 0
