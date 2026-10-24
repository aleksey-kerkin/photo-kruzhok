import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.access import issue_access_token
from accounts.hashes import hash_token
from accounts.models import Profile, RefreshToken

User = get_user_model()


def _set_refresh_cookie(response, raw):
    response.set_cookie(
        "pk_refresh",
        raw,
        max_age=7 * 24 * 60 * 60,
        httponly=True,
        secure=True,
        samesite="Lax",
        path="/api/auth",
    )


def _issue_refresh(user):
    raw = secrets.token_urlsafe(32)
    RefreshToken.objects.create(
        user=user,
        token_hash=hash_token(raw),
        expires_at=timezone.now() + timedelta(days=7),
    )
    return raw


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password") or ""
        fields = {}
        if not 5 <= len(username) <= 30:
            fields["username"] = ["Username must be 5 to 30 characters."]
        elif User.objects.filter(username=username).exists():
            fields["username"] = ["A user with that username already exists."]
        if not email:
            fields["email"] = ["This field is required."]
        elif User.objects.filter(email=email).exists():
            fields["email"] = ["A user with that email already exists."]
        try:
            validate_password(password)
        except Exception as exc:
            fields["password"] = [str(item) for item in getattr(exc, "messages", [exc])]
        if fields:
            raise ValidationError(fields)
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user)
        response = Response({"access": issue_access_token(user)}, status=201)
        _set_refresh_cookie(response, _issue_refresh(user))
        return response
