import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    database_url: str = "sqlite:///./data/plaza.db"
    app_env: str = "development"
    cookie_secure: bool = False
    session_hours: int = 8
    allowed_hosts: tuple[str, ...] = ("localhost", "127.0.0.1", "testserver")

    def __post_init__(self):
        if self.app_env not in {"development", "test", "production"}:
            raise ValueError("APP_ENV debe ser development, test o production")
        if not 1 <= self.session_hours <= 24:
            raise ValueError("SESSION_HOURS debe estar entre 1 y 24")
        if not self.allowed_hosts or "*" in self.allowed_hosts:
            raise ValueError("ALLOWED_HOSTS debe enumerar hosts explícitos")
        if self.app_env == "production":
            if not self.cookie_secure or not self.database_url.startswith("postgresql+psycopg://"):
                raise ValueError("Producción requiere PostgreSQL y COOKIE_SECURE=true")

    @classmethod
    def from_env(cls):
        load_dotenv()
        secure = os.getenv("COOKIE_SECURE", "false").lower()
        if secure not in {"true", "false"}:
            raise ValueError("COOKIE_SECURE debe ser true o false")
        return cls(
            database_url=os.getenv("DATABASE_URL", cls.database_url),
            app_env=os.getenv("APP_ENV", "development"),
            cookie_secure=secure == "true",
            session_hours=int(os.getenv("SESSION_HOURS", "8")),
            allowed_hosts=tuple(h.strip() for h in os.getenv(
                "ALLOWED_HOSTS", "localhost,127.0.0.1,testserver"
            ).split(",") if h.strip()),
        )
