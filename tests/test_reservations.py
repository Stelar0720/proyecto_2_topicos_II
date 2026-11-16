"""HU-01 · AC-01/02/03/07/13 sobre disponibilidad y reserva preferencial."""
import re
import threading
from datetime import timedelta

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from plaza_reserva.cli import seed_spaces
from plaza_reserva.errors import AppError
from plaza_reserva.models import Allocation, Reservation, Space, Stay
from plaza_reserva.reservations import create_reservation, effective_availability
from plaza_reserva.security import new_token, token_digest

ORIGIN = {"Origin": "http://testserver"}
CODE_PATTERN = re.compile(r"<code>([A-Za-z0-9_-]{43})</code>")


def seed(engine):
    with Session(engine) as session:
        seed_spaces(session)


def reserve(client, plate):
    return client.post("/api/reservations", json={"plate": plate}, headers=ORIGIN)


def counts(engine):
    with Session(engine) as session:
        return (session.scalar(select(func.count()).select_from(Reservation)),
                session.scalar(select(func.count()).select_from(Allocation)))


def fill_preferential(client, total):
    for index in range(total):
        response = reserve(client, f"FILL{index:02d}")
        assert response.status_code == 201, response.text


def test_availability_reports_effective_capacity_without_visitor_data(client, engine):
    seed(engine)
    payload = client.get("/api/availability").json()
    assert payload["preferential"] == {"available": 20, "total": 20}
    assert payload["general"] == {"available": 80, "total": 80}
    assert payload["as_of"].endswith("Z") or "+00:00" in payload["as_of"]
    assert set(payload) == {"as_of", "preferential", "general"}


def test_reservation_holds_preferential_for_thirty_minutes(client, engine, clock):
    seed(engine)
    response = reserve(client, " abc-123 ")
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["space_code"] == "P001"
    assert len(body["private_code"]) == 43
    with Session(engine) as session:
        stored = session.scalar(select(Reservation))
        assert stored.plate == "ABC-123"
        assert stored.expires_at - stored.created_at == timedelta(minutes=30)
        assert stored.created_at == clock.value
        assert stored.token_hash == token_digest(body["private_code"])
        assert body["private_code"] != stored.token_hash
        assert session.get(Allocation, "P001").reservation_id == stored.id
    assert response.headers["cache-control"] == "no-store"
    assert client.get("/api/availability").json()["preferential"]["available"] == 19


def test_expiry_at_exact_instant_is_ignored_without_cron(client, engine, clock):
    seed(engine)
    assert reserve(client, "ABC123").status_code == 201
    clock.value += timedelta(minutes=30)
    assert client.get("/api/availability").json()["preferential"]["available"] == 20
    with Session(engine) as session:
        assert session.scalar(select(Reservation.status)) == "pending"
    again = reserve(client, "ABC123")
    assert again.status_code == 201, again.text
    assert again.json()["space_code"] == "P001"
    with Session(engine) as session:
        assert sorted(session.scalars(select(Reservation.status)).all()) == ["expired", "pending"]


def test_duplicate_pending_plate_is_rejected(client, engine):
    seed(engine)
    assert reserve(client, "DUP-01").status_code == 201
    conflict = reserve(client, "dup-01")
    assert conflict.status_code == 409
    assert conflict.json()["error"]["code"] == "PLATE_BUSY"
    assert counts(engine) == (1, 1)


def test_plate_with_open_stay_cannot_reserve(client, engine, clock):
    seed(engine)
    with Session(engine) as session:
        stay = Stay(plate="EST-01", space_id="G001", ticket_hash=token_digest(new_token()),
                    status="open", entered_at=clock.value)
        session.add(stay)
        session.flush()
        session.add(Allocation(space_id="G001", plate="EST-01", stay_id=stay.id))
        session.commit()
    response = reserve(client, "EST-01")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PLATE_BUSY"
    assert counts(engine) == (0, 1)


@pytest.mark.parametrize("plate", ["A", "ABC 123", "PLACA.CON.PUNTO", "X" * 13, "  "])
def test_invalid_plate_is_a_validation_error(client, engine, plate):
    seed(engine)
    response = reserve(client, plate)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert counts(engine) == (0, 0)


def test_category_full_leaves_no_partial_records(client, engine):
    seed(engine)
    fill_preferential(client, 20)
    rejected = reserve(client, "FULL01")
    assert rejected.status_code == 409
    assert rejected.json()["error"]["code"] == "CATEGORY_FULL"
    assert counts(engine) == (20, 20)
    payload = client.get("/api/availability").json()
    assert payload["preferential"]["available"] == 0
    assert payload["general"]["available"] == 80


def run_concurrently(calls):
    barrier = threading.Barrier(len(calls))
    results = []

    def wrap(call):
        barrier.wait()
        try:
            results.append(("ok", call()))
        except AppError as exc:
            results.append(("error", exc.code))

    threads = [threading.Thread(target=wrap, args=(call,)) for call in calls]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=20)
    assert not any(thread.is_alive() for thread in threads)
    return results


def reserve_with_new_session(engine, clock, plate):
    def call():
        with Session(engine) as session:
            return create_reservation(session, clock.value, plate)
    return call


def test_simultaneous_requests_for_last_preferential_single_winner(client, engine, clock):
    seed(engine)
    fill_preferential(client, 19)
    results = run_concurrently([
        reserve_with_new_session(engine, clock, "RACE01"),
        reserve_with_new_session(engine, clock, "RACE02"),
    ])
    assert sorted(result[0] for result in results) == ["error", "ok"]
    assert [result[1] for result in results if result[0] == "error"] == ["CATEGORY_FULL"]
    assert counts(engine) == (20, 20)


def test_simultaneous_requests_same_plate_single_reservation(engine, clock):
    seed(engine)
    results = run_concurrently([
        reserve_with_new_session(engine, clock, "SAMEP1"),
        reserve_with_new_session(engine, clock, "SAMEP1"),
    ])
    assert sorted(result[0] for result in results) == ["error", "ok"]
    assert [result[1] for result in results if result[0] == "error"] == ["PLATE_BUSY"]
    assert counts(engine) == (1, 1)


def test_mutations_require_same_origin(client, engine):
    seed(engine)
    assert client.post("/api/reservations", json={"plate": "ORIG01"}).status_code == 403
    foreign = client.post("/api/reservations", json={"plate": "ORIG01"},
                          headers={"Origin": "https://ajeno.invalid"})
    assert foreign.status_code == 403
    assert foreign.json()["error"]["code"] == "ORIGIN_REQUIRED"
    assert client.post("/reservar", data={"plate": "ORIG01"}).status_code == 403
    assert counts(engine) == (0, 0)


def test_form_post_accepts_browser_same_origin_signal(client, engine):
    """Chrome envía `Origin: null` por `Referrer-Policy: no-referrer`; Sec-Fetch-Site decide."""
    seed(engine)
    chrome_form = {"Origin": "null", "Sec-Fetch-Site": "same-origin"}
    page = client.post("/reservar", data={"plate": "FORM01"}, headers=chrome_form)
    assert page.status_code == 200, page.text
    assert CODE_PATTERN.search(page.text)
    cross_site = client.post("/api/reservations", json={"plate": "FORM02"},
                             headers={"Origin": "null", "Sec-Fetch-Site": "cross-site"})
    assert cross_site.status_code == 403
    null_only = client.post("/api/reservations", json={"plate": "FORM03"},
                            headers={"Origin": "null"})
    assert null_only.status_code == 403
    assert counts(engine) == (1, 1)


def test_availability_view_shows_capacity_and_form(client, engine):
    seed(engine)
    page = client.get("/reservar")
    assert page.status_code == 200
    assert "Preferenciales libres" in page.text
    assert 'name="plate"' in page.text
    assert "30" in page.text


def test_form_creates_reservation_with_qr_and_private_code(client, engine):
    seed(engine)
    page = client.post("/reservar", data={"plate": "TICK01"}, headers=ORIGIN)
    assert page.status_code == 200
    assert page.headers["cache-control"] == "no-store"
    assert "P001" in page.text
    match = CODE_PATTERN.search(page.text)
    assert match, page.text
    private_code = match.group(1)
    svg = re.search(r"<svg.*?</svg>", page.text, re.S).group(0)
    assert "TICK01" not in svg
    with Session(engine) as session:
        assert session.scalar(select(Reservation.token_hash)) == token_digest(private_code)
    assert client.get("/api/availability").json()["preferential"]["available"] == 19


def test_form_reports_conflict_without_creating_records(client, engine):
    seed(engine)
    fill_preferential(client, 20)
    page = client.post("/reservar", data={"plate": "FULL02"}, headers=ORIGIN)
    assert page.status_code == 409
    assert "No se pudo reservar" in page.text
    assert counts(engine) == (20, 20)


def test_effective_availability_ignores_expired_without_writing(engine, clock):
    seed(engine)
    with Session(engine) as session:
        space = session.get(Space, "P001")
        session.add(Reservation(plate="VIEW01", space_id=space.code, status="pending",
                                token_hash=token_digest(new_token()),
                                created_at=clock.value - timedelta(minutes=40),
                                expires_at=clock.value - timedelta(minutes=10)))
        session.flush()
        session.add(Allocation(space_id=space.code, plate="VIEW01",
                               reservation_id=session.scalar(select(Reservation.id))))
        session.commit()
        data = effective_availability(session, clock.value)
        assert data["preferential"]["available"] == 20
        assert session.scalar(select(Reservation.status)) == "pending"
