import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_schema_lists_session_paths():
    response = APIClient().get("/api/schema/")
    assert response.status_code == 200
    paths = response.json()["paths"]
    for path in (
        "/api/health",
        "/api/auth/register",
        "/api/auth/login",
        "/api/auth/refresh",
        "/api/auth/logout",
        "/api/auth/me",
    ):
        assert path in paths
