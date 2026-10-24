import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_login_accepts_email(member):
    response = APIClient().post(
        "/api/auth/login",
        {"username": "anya@example.com", "password": "correct-horse-battery"},
        format="json",
    )
    assert response.status_code == 200
    assert response.json()["access"]
    assert response.cookies["pk_refresh"].value


@pytest.mark.django_db
def test_login_accepts_email_case_insensitive(member):
    response = APIClient().post(
        "/api/auth/login",
        {"username": "ANYA@EXAMPLE.COM", "password": "correct-horse-battery"},
        format="json",
    )
    assert response.status_code == 200
    assert response.json()["access"]


@pytest.mark.django_db
def test_login_rejects_a_bad_password(member):
    response = APIClient().post(
        "/api/auth/login",
        {"username": "anya01", "password": "wrong-password-here"},
        format="json",
    )
    assert response.status_code == 401
    assert response.json()["code"] == "not_authenticated"
    assert response.json()["fields"] == {}
