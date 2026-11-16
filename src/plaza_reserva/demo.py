"""HU-04/HU-05/QA-01 - seed de datos demo idempotente en BD separada.

Referencia comun 2026-11-15T17:00:00Z (12:00 Panama). Seis escenarios de docs/testing.md.
Usa IDs estables de namespace demo; no borra datos ajenos; segunda carga no duplica.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from .db import allocation_transaction, build_engine
from .models import Allocation, Payment, Reservation, Space, Stay
from .security import token_digest

DEMO_REFERENCE = datetime(2026, 11, 15, 17, 0, tzinfo=timezone.utc)
DEMO_IDS = {
    "reservation_vigente": "demo-reservation-vigente",
    "reservation_vencida": "demo-reservation-vencida",
    "stay_abierta": "demo-stay-abierta",
    "stay_larga": "demo-stay-larga",
    "stay_cobro": "demo-stay-cobro",
    "stay_cerrada": "demo-stay-cerrada",
    "payment_cerrada": "demo-payment-cerrada",
    "staff": "demo-staff-admin",
}
DEMO_HASHES = {k: token_digest(f"demo-secret-{k}") for k in [
    "reservation_vigente", "reservation_vencida", "stay_abierta", "stay_larga", "stay_cobro", "stay_cerrada",
]}
DEMO_PLATES = {"DEMO01", "DEMO02", "DEMO03", "DEMO04", "DEMO05", "DEMO06"}
DEMO_SPACES = {"P001", "P002", "G001", "G002", "G003", "G004"}


def _ensure_staff(session: Session):
    from .models import Staff
    existing = session.get(Staff, DEMO_IDS["staff"])
    if existing:
        return existing
    staff = Staff(id=DEMO_IDS["staff"], username="demo_admin", role="admin",
                  password_hash="!" * 60, active=False, created_at=DEMO_REFERENCE)
    session.add(staff)
    return staff


def _scenario_rows():
    ref = DEMO_REFERENCE
    return {
        "reservation_vigente": dict(
            reservation=Reservation(id=DEMO_IDS["reservation_vigente"], plate="DEMO01", space_id="P001",
                                   status="pending", token_hash=DEMO_HASHES["reservation_vigente"],
                                   created_at=ref - timedelta(minutes=5), expires_at=ref + timedelta(minutes=25)),
            allocation=Allocation(space_id="P001", plate="DEMO01", reservation_id=DEMO_IDS["reservation_vigente"]),
        ),
        "reservation_vencida": dict(
            reservation=Reservation(id=DEMO_IDS["reservation_vencida"], plate="DEMO02", space_id="P002",
                                   status="expired", token_hash=DEMO_HASHES["reservation_vencida"],
                                   created_at=ref - timedelta(minutes=40), expires_at=ref - timedelta(minutes=10)),
            allocation=None,
        ),
        "stay_abierta": dict(
            stay=Stay(id=DEMO_IDS["stay_abierta"], plate="DEMO03", space_id="G001",
                      ticket_hash=DEMO_HASHES["stay_abierta"], status="open",
                      entered_at=ref - timedelta(minutes=10)),
            allocation=Allocation(space_id="G001", plate="DEMO03", stay_id=DEMO_IDS["stay_abierta"]),
        ),
        "stay_larga": dict(
            stay=Stay(id=DEMO_IDS["stay_larga"], plate="DEMO04", space_id="G002",
                      ticket_hash=DEMO_HASHES["stay_larga"], status="open",
                      entered_at=ref - timedelta(hours=25)),
            allocation=Allocation(space_id="G002", plate="DEMO04", stay_id=DEMO_IDS["stay_larga"]),
        ),
        "stay_cobro": dict(
            stay=Stay(id=DEMO_IDS["stay_cobro"], plate="DEMO05", space_id="G003",
                      ticket_hash=DEMO_HASHES["stay_cobro"], status="open",
                      entered_at=ref - timedelta(minutes=65)),
            allocation=Allocation(space_id="G003", plate="DEMO05", stay_id=DEMO_IDS["stay_cobro"]),
        ),
        "stay_cerrada": dict(
            stay=Stay(id=DEMO_IDS["stay_cerrada"], plate="DEMO06", space_id="G004",
                      ticket_hash=DEMO_HASHES["stay_cerrada"], status="closed",
                      entered_at=ref - timedelta(minutes=120), exited_at=ref - timedelta(minutes=60)),
            allocation=None,
            payment=Payment(id=DEMO_IDS["payment_cerrada"], stay_id=DEMO_IDS["stay_cerrada"],
                            amount_cents=120, paid_at=ref - timedelta(minutes=60),
                            staff_id=DEMO_IDS["staff"], idempotency_key="demo-idem-cerrada"),
        ),
    }


def seed_demo(session: Session) -> dict:
    """Inserta los 6 escenarios si faltan; aborta sin cambios ante colision ajena."""
    from sqlalchemy import exists, select
    from .models import Staff
    scenarios = _scenario_rows()
    with allocation_transaction(session):
        # detectar si ya esta todo el namespace demo
        demo_res = set(session.scalars(select(Reservation.id).where(Reservation.id.in_(list(DEMO_IDS.values())))).all())
        demo_stays = set(session.scalars(select(Stay.id).where(Stay.id.in_(list(DEMO_IDS.values())))).all())
        demo_pay = session.get(Payment, DEMO_IDS["payment_cerrada"]) is not None
        already = (DEMO_IDS["reservation_vigente"] in demo_res and
                   DEMO_IDS["reservation_vencida"] in demo_res and
                   DEMO_IDS["stay_abierta"] in demo_stays and
                   DEMO_IDS["stay_larga"] in demo_stays and
                   DEMO_IDS["stay_cobro"] in demo_stays and
                   DEMO_IDS["stay_cerrada"] in demo_stays and demo_pay)
        if already:
            return {"status": "noop", "inserted": 0}

        # colisiones con datos ajenos (mismas placas/espacios/ids no-demo)
        for sid in DEMO_SPACES:
            alloc = session.get(Allocation, sid)
            if alloc is not None:
                # permitido solo si pertenece a escenario demo
                allowed = {DEMO_IDS["reservation_vigente"], DEMO_IDS["stay_abierta"], DEMO_IDS["stay_larga"], DEMO_IDS["stay_cobro"]}
                if alloc.reservation_id not in allowed and alloc.stay_id not in allowed:
                    raise ValueError(f"Colision con datos ajenos en espacio {sid}; abortado")
        for plate in DEMO_PLATES:
            r = session.scalar(select(Reservation).where(Reservation.plate == plate))
            if r and r.id not in DEMO_IDS.values():
                raise ValueError(f"Colision con datos ajenos en placa {plate}; abortado")
            s = session.scalar(select(Stay).where(Stay.plate == plate))
            if s and s.id not in DEMO_IDS.values():
                raise ValueError(f"Colision con datos ajenos en placa {plate}; abortado")

        staff = _ensure_staff(session)
        session.flush()
        inserted = 0
        # reservas
        for key in ("reservation_vigente", "reservation_vencida"):
            sc = scenarios[key]
            if session.get(Reservation, sc["reservation"].id) is None:
                session.add(sc["reservation"])
                session.flush()
                if sc["allocation"] is not None:
                    session.add(sc["allocation"])
                inserted += 1
        # estadias
        for key in ("stay_abierta", "stay_larga", "stay_cobro", "stay_cerrada"):
            sc = scenarios[key]
            if session.get(Stay, sc["stay"].id) is None:
                session.add(sc["stay"])
                session.flush()
                if sc["allocation"] is not None:
                    session.add(sc["allocation"])
                if sc.get("payment") is not None:
                    session.add(sc["payment"])
                inserted += 1
    return {"status": "inserted", "inserted": inserted}


def seed_demo_database(database_url: str) -> dict:
    from alembic import command
    from alembic.config import Config
    from .cli import seed_spaces
    engine = build_engine(database_url)
    try:
        config = Config("alembic.ini")
        with engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")
        with Session(engine) as session:
            seed_spaces(session)
        with Session(engine) as session:
            return seed_demo(session)
    finally:
        engine.dispose()
