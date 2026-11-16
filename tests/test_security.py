from datetime import datetime

import pytest

from plaza_reserva.config import Settings
from plaza_reserva.models import UTCDateTime
from plaza_reserva.security import hash_password, new_token, token_digest, verify_password


def test_password_salted_and_verified():
    password = "credencial-solo-test"
    first = hash_password(password)
    second = hash_password(password)
    assert first != second
    assert verify_password(password, first)
    assert not verify_password("otra-credencial", first)
    assert password not in first


def test_random_tokens_not_personal_data():
    first, second = new_token(), new_token()
    assert first != second
    assert len(first) >= 43
    assert len(token_digest(first)) == 64


def test_naive_timestamp_rejected():
    with pytest.raises(ValueError):
        UTCDateTime().process_bind_param(datetime(2026, 1, 1), None)


def test_production_configuration_requires_secure_postgresql():
    with pytest.raises(ValueError):
        Settings(app_env="production")
