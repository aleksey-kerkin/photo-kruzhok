import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from accounts.access import issue_access_token
from accounts.authentication import AccessTokenAuthentication

User = get_user_model()


@pytest.mark.django_db
def test_access_token_authentication_returns_none_without_header():
    auth = AccessTokenAuthentication()
    request = APIRequestFactory().get("/api/posts")
    assert auth.authenticate(request) is None


@pytest.mark.django_db
def test_access_token_authentication_returns_user_for_valid_bearer(member):
    token = issue_access_token(member)
    auth = AccessTokenAuthentication()
    request = APIRequestFactory().get(
        "/api/posts",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )
    user, payload = auth.authenticate(request)
    assert user == member
    assert payload["sub"] == str(member.pk)


@pytest.mark.django_db
def test_access_token_authentication_returns_none_for_empty_bearer_value():
    auth = AccessTokenAuthentication()
    request = APIRequestFactory().get(
        "/api/posts",
        HTTP_AUTHORIZATION="Bearer    ",
    )
    assert auth.authenticate(request) is None


@pytest.mark.django_db
def test_access_token_authentication_returns_none_for_invalid_token():
    auth = AccessTokenAuthentication()
    request = APIRequestFactory().get(
        "/api/posts",
        HTTP_AUTHORIZATION="Bearer not-a-valid-token",
    )
    assert auth.authenticate(request) is None


@pytest.mark.django_db
def test_access_token_authentication_returns_none_when_sub_is_missing(monkeypatch):
    monkeypatch.setattr("accounts.authentication.read_access_token", lambda raw: {})
    auth = AccessTokenAuthentication()
    request = APIRequestFactory().get(
        "/api/posts",
        HTTP_AUTHORIZATION="Bearer token",
    )
    assert auth.authenticate(request) is None


@pytest.mark.django_db
def test_access_token_authentication_returns_none_for_unknown_user():
    token = issue_access_token(User(id=999_999))
    auth = AccessTokenAuthentication()
    request = APIRequestFactory().get(
        "/api/posts",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )
    assert auth.authenticate(request) is None
