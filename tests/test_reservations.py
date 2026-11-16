"""T-01A · Disponibilidad efectiva y vista de reserva (AC-03)."""
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from plaza_reserva.cli import seed_spaces
from plaza_reserva.models import Allocation, Reservation
from plaza_reserva.reservations import effective_availability
from plaza_reserva.security import new_token, token_digest


def seed(engine):
    with Session(engine) as session:
        seed_spaces(session)


def test_availability_reports_effective_capacity_without_visitor_data(client, engine):
    seed(engine)
    payload = client.get("/api/availability").json()
    assert payload["preferential"] == {"available": 20, "total": 20}
    assert payload["general"] == {"available": 80, "total": 80}
    assert payload["as_of"].endswith("Z") or "+00:00" in payload["as_of"]
    assert set(payload) == {"as_of", "preferential", "general"}


def test_availability_view_shows_capacity_and_form(client, engine):
    seed(engine)
    page = client.get("/reservar")
    assert page.status_code == 200
    assert "Preferenciales libres" in page.text
    assert 'name="plate"' in page.text
    assert "30" in page.text


def test_effective_availability_ignores_expired_without_writing(engine, clock):
    seed(engine)
    with Session(engine) as session:
        session.add(Reservation(plate="VIEW01", space_id="P001", status="pending",
                                token_hash=token_digest(new_token()),
                                created_at=clock.value - timedelta(minutes=40),
                                expires_at=clock.value - timedelta(minutes=10)))
        session.flush()
        session.add(Allocation(space_id="P001", plate="VIEW01",
                               reservation_id=session.scalar(select(Reservation.id))))
        session.commit()
        data = effective_availability(session, clock.value)
        assert data["preferential"]["available"] == 20
        assert session.scalar(select(Reservation.status)) == "pending"
