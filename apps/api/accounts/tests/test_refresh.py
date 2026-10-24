import pytest
from rest_framework.test import APIClient

from accounts.hashes import hash_token
from accounts.models import RefreshToken


@pytest.mark.django_db
def test_refresh_rotates_the_cookie(member):
    client = APIClient()
    first = client.post(
        "/api/auth/login",
        {"username": "anya01", "password": "correct-horse-battery"},
        format="json",
    )
    old = first.cookies["pk_refresh"].value
    client.cookies["pk_refresh"] = old
    second = client.post("/api/auth/refresh")
    assert second.status_code == 200
    new = second.cookies["pk_refresh"].value
    assert new and new != old
    assert not RefreshToken.objects.filter(token_hash=hash_token(old)).exists()
    assert RefreshToken.objects.filter(token_hash=hash_token(new)).exists()


@pytest.mark.django_db
def test_refresh_without_cookie_is_unauthenticated():
    response = APIClient().post("/api/auth/refresh")
    assert response.status_code == 401
    assert response.json()["code"] == "not_authenticated"
