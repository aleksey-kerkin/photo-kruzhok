import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_register_sets_refresh_cookie_and_profile():
    response = APIClient().post(
        "/api/auth/register",
        {
            "username": "anya01",
            "email": "anya@example.com",
            "password": "correct-horse-battery",
        },
        format="json",
    )
    assert response.status_code == 201
    assert response.json()["access"]
    cookie = response.cookies["pk_refresh"]
    assert cookie.value
    assert cookie["httponly"]
    assert cookie["samesite"] == "Lax"
    assert cookie["path"] == "/api/auth"
    user = get_user_model().objects.get(username="anya01")
    assert user.profile.is_leader is False


@pytest.mark.django_db
def test_register_rejects_a_short_username():
    response = APIClient().post(
        "/api/auth/register",
        {
            "username": "ann",
            "email": "ann@example.com",
            "password": "correct-horse-battery",
        },
        format="json",
    )
    assert response.status_code == 400
    assert response.json()["code"] == "validation_error"
    assert "username" in response.json()["fields"]
