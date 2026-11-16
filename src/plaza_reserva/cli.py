import argparse
import getpass
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from .clock import SystemClock
from .config import Settings
from .db import allocation_transaction, build_engine
from .models import Space, Staff
from .security import hash_password


def seed_spaces(session: Session) -> int:
    """Agrega faltantes; jamás actualiza/borrar registros existentes."""
    inserted = 0
    with allocation_transaction(session):
        for prefix, total, category in (("P", 20, "preferential"), ("G", 80, "general")):
            for i in range(1, total + 1):
                code = f"{prefix}{i:03}"
                existing = session.get(Space, code)
                if existing is not None:
                    if existing.category != category:
                        raise ValueError(f"Categoría existente incompatible en {code}; no se modificó")
                    continue
                session.add(Space(code=code, category=category))
                inserted += 1
    return inserted


def create_staff(session: Session, username: str, role: str, password: str, clock=None):
    username = username.strip().lower()
    if not re.fullmatch(r"[a-z0-9_.-]{3,80}", username):
        raise ValueError("Usuario: 3–80 letras minúsculas, números, punto, guion o guion bajo")
    if role not in {"admin", "client"}:
        raise ValueError("Rol inválido")
    if session.scalar(select(Staff).where(Staff.username == username)):
        raise ValueError("El usuario ya existe; no se cambió su contraseña")
    staff = Staff(username=username, role=role, password_hash=hash_password(password),
                  active=True, created_at=(clock or SystemClock()).now())
    session.add(staff)
    session.commit()
    return staff


def main():
    parser = argparse.ArgumentParser(description="Administración local de Plaza Reserva")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("seed-spaces", help="Agregar los 100 espacios de forma idempotente")
    staff = commands.add_parser("create-staff", help="Alta de personal sin contrasena en argumentos")
    staff.add_argument("--username", required=True)
    staff.add_argument("--role", choices=["admin", "client"], required=True)
    demo = commands.add_parser("seed-demo", help="Cargar 6 escenarios demo idempotentes en BD separada")
    demo.add_argument("--database-url", default=None, help="URL de BD destino (por defecto sqlite:///data/plaza_demo.db)")
    args = parser.parse_args()
    if args.command == "seed-demo":
        from .demo import seed_demo_database
        db_url = args.database_url or "sqlite:///data/plaza_demo.db"
        if db_url == Settings.from_env().database_url and "plaza_demo" not in db_url:
            parser.exit(1, "seed-demo debe ejecutarse en una BD separada (use --database-url o data/plaza_demo.db)\n")
        try:
            result = seed_demo_database(db_url)
            print(f"Demo: {result['status']} (inserted={result['inserted']}) en {db_url}")
        except ValueError as exc:
            parser.exit(1, f"{exc}\n")
        return
    engine = build_engine(Settings.from_env().database_url)
    try:
        with Session(engine) as session:
            if args.command == "seed-spaces":
                print(f"Espacios agregados: {seed_spaces(session)}")
            else:
                password = getpass.getpass("Contrasena (4-10 caracteres): ")
                if password != getpass.getpass("Repite contrasena: "):
                    parser.exit(1, "Las contrasenas no coinciden\n")
                if not 4 <= len(password) <= 10:
                    parser.exit(1, "La contrasena debe tener 4-10 caracteres\n")
                create_staff(session, args.username, args.role, password)
                print("Personal creado; contrasena no registrada")
    except ValueError as exc:
        parser.exit(1, f"{exc}\n")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
