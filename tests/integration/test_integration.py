"""QA-01 / integracion: carreras y escenarios demo con DB real."""
import threading
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from plaza_reserva.cli import create_staff, seed_spaces
from plaza_reserva.demo import DEMO_REFERENCE, seed_demo
from plaza_reserva.entries import enter_walk_in
from plaza_reserva.errors import AppError
from plaza_reserva.exits import close_stay, quote_amount_cents
from plaza_reserva.models import Allocation, Payment, Reservation, Stay
from plaza_reserva.reservations import create_reservation

PASSWORD = "solo-para-prueba-aleatoria"


def seed(engine):
    with Session(engine) as session:
        seed_spaces(session)


def test_last_general_walkin_race_single_winner(engine, clock):
    seed(engine)
    # ocupar 79 generales
    with Session(engine) as session:
        for i in range(1, 80):
            enter_walk_in(session, clock.value, f"PRE{i:03d}")
    barrier = threading.Barrier(2)
    results = []
    def worker(plate):
        barrier.wait()
        try:
            with Session(engine) as session:
                results.append(("ok", enter_walk_in(session, clock.value, plate)["space_code"]))
        except AppError as exc:
            results.append(("error", exc.code))
    threads = [threading.Thread(target=worker, args=(p,)) for p in ("RACEA1", "RACEB2")]
    for t in threads: t.start()
    for t in threads: t.join(timeout=20)
    assert sorted(r[0] for r in results) == ["error", "ok"]
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(Allocation)) == 80


def test_last_preferential_reservation_race_single_winner(engine, clock):
    seed(engine)
    # ocupar 19 preferenciales
    for i in range(1, 20):
        with Session(engine) as session:
            create_reservation(session, clock.value, f"RP{i:03d}")
    barrier = threading.Barrier(2)
    results = []
    def worker(plate):
        barrier.wait()
        try:
            with Session(engine) as session:
                results.append(("ok", create_reservation(session, clock.value, plate)["space_code"]))
        except AppError as exc:
            results.append(("error", exc.code))
    threads = [threading.Thread(target=worker, args=(p,)) for p in ("RACEP1", "RACEP2")]
    for t in threads: t.start()
    for t in threads: t.join(timeout=20)
    assert sorted(r[0] for r in results) == ["error", "ok"]
    with Session(engine) as session:
        pref_allocs = session.scalars(select(Allocation.space_id)).all()
        assert len([s for s in pref_allocs if s.startswith("P")]) == 20


def test_demo_seed_idempotent_and_scenarios(engine, clock):
    seed(engine)
    with Session(engine) as session:
        first = seed_demo(session)
        assert first["status"] == "inserted"
    with Session(engine) as session:
        second = seed_demo(session)
        assert second["status"] == "noop"
    ref = DEMO_REFERENCE
    with Session(engine) as session:
        # vigente
        r1 = session.get(Reservation, "demo-reservation-vigente")
        assert r1 and r1.status == "pending" and r1.plate == "DEMO01"
        assert session.get(Allocation, "P001").reservation_id == r1.id
        # vencida sin allocation
        r2 = session.get(Reservation, "demo-reservation-vencida")
        assert r2.status == "expired" and session.get(Allocation, "P002") is None
        # abiertas
        s3 = session.get(Stay, "demo-stay-abierta")
        assert s3.status == "open" and session.get(Allocation, "G001").stay_id == s3.id
        s4 = session.get(Stay, "demo-stay-larga")
        assert (ref - s4.entered_at) > timedelta(hours=24)
        s5 = session.get(Stay, "demo-stay-cobro")
        assert quote_amount_cents(s5.entered_at, ref) == 130
        # cerrada/pagada
        s6 = session.get(Stay, "demo-stay-cerrada")
        p6 = session.scalar(select(Payment).where(Payment.stay_id == s6.id))
        assert s6.status == "closed" and p6.amount_cents == 120
        assert session.get(Allocation, "G004") is None
