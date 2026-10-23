import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_unknown_api_path_uses_the_error_envelope():
    response = APIClient().get("/api/does-not-exist")
    assert response.status_code == 404
    assert set(response.json()) == {"code", "message", "fields"}
    assert response.json()["code"] == "not_found"
    assert response.json()["fields"] == {}


@pytest.mark.django_db
def test_posts_route_is_not_handled_by_api_catch_all(client):
    client.raise_request_exception = False
    response = client.get("/posts/")
    assert b'"code": "not_found"' not in response.content
    assert b'"code":"not_found"' not in response.content
