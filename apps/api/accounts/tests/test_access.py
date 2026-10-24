from datetime import datetime, timezone

import jwt
import pytest
from django.contrib.auth import get_user_model

from accounts.access import issue_access_token, read_access_token


@pytest.mark.django_db
def test_access_token_expires_in_fifteen_minutes(settings):
    settings.SECRET_KEY = "test-secret-key"
    user = get_user_model().objects.create_user(
        username="anya01", email="anya@example.com", password="correct-horse-battery"
    )
    raw = issue_access_token(user)
    payload = read_access_token(raw)
    assert payload["sub"] == str(user.id)
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    remaining = exp - datetime.now(timezone.utc)
    assert 14 * 60 < remaining.total_seconds() < 16 * 60
    with pytest.raises(jwt.InvalidTokenError):
        read_access_token(raw + "x")
