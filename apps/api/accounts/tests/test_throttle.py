import pytest
from django.core.cache import cache
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_login_is_limited_to_five_attempts_per_minute():
    cache.clear()
    client = APIClient()
    last = None
    for _ in range(6):
        last = client.post(
            "/api/auth/login",
            {"username": "nobody", "password": "wrong-password-here"},
            format="json",
        )
    assert last.status_code == 429
    assert last.json()["code"] == "too_many_requests"
