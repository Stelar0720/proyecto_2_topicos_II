"""Secretos fuera de logs. Sin contraseñas predeterminadas."""
import base64
import hashlib
import hmac
import secrets

ITERATIONS = 600_000


def hash_password(password: str) -> str:
    if not 4 <= len(password) <= 128:
        raise ValueError("La contraseña requiere entre 4 y 128 caracteres")
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return "$".join(("pbkdf2_sha256", str(ITERATIONS),
                     base64.b64encode(salt).decode(), base64.b64encode(digest).decode()))


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, expected = encoded.split("$")
        count = int(iterations)
        if algorithm != "pbkdf2_sha256" or not 600_000 <= count <= 2_000_000:
            return False
        # Las nuevas cuentas usan 4–10 caracteres. Aceptamos hashes previos con
        # contraseñas más largas para no bloquear al administrador ya existente.
        if not 4 <= len(password) <= 128:
            return False
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.b64decode(salt), count)
        return hmac.compare_digest(actual, base64.b64decode(expected))
    except (ValueError, TypeError):
        return False


def token_digest(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def new_token() -> str:
    return secrets.token_urlsafe(32)
