from accounts.authentication import AccessTokenAuthentication


def test_authenticate_header_returns_bearer():
    auth = AccessTokenAuthentication()
    assert auth.authenticate_header(None) == "Bearer"
