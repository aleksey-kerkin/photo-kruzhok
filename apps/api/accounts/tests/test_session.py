import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_me_returns_the_profile_and_logout_clears_the_cookie(member):
    client = APIClient()
    logged_in = client.post(
        "/api/auth/login",
        {"username": "anya01", "password": "correct-horse-battery"},
        format="json",
    )
    access = logged_in.json()["access"]
    me = client.get("/api/auth/me", HTTP_AUTHORIZATION=f"Bearer {access}")
    assert me.status_code == 200
    assert me.json()["username"] == "anya01"
    assert me.json()["is_leader"] is False
    client.cookies["pk_refresh"] = logged_in.cookies["pk_refresh"].value
    logged_out = client.post("/api/auth/logout")
    assert logged_out.status_code == 204
    assert logged_out.cookies["pk_refresh"].value == ""
