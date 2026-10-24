import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from accounts.access import issue_access_token
from accounts.hashes import hash_token
from accounts.models import Profile, RefreshToken

User = get_user_model()


class _LoginAuthentication(BaseAuthentication):
    def authenticate(self, request):
        return None

    def authenticate_header(self, request):
        return "Bearer"


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


class LoginView(APIView):
    authentication_classes = [_LoginAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        value = (request.data.get("username") or "").strip()
        password = request.data.get("password") or ""
        if "@" in value:
            user = User.objects.filter(email=value.lower()).first()
        else:
            user = User.objects.filter(username=value).first()
        if user is None or not user.check_password(password):
            raise AuthenticationFailed()
        response = Response({"access": issue_access_token(user)})
        _set_refresh_cookie(response, _issue_refresh(user))
        return response


class RefreshView(APIView):
    authentication_classes = [_LoginAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        raw = request.COOKIES.get("pk_refresh")
        if not raw:
            raise AuthenticationFailed()
        refresh = RefreshToken.objects.filter(token_hash=hash_token(raw)).first()
        if refresh is None or refresh.expires_at <= timezone.now():
            raise AuthenticationFailed()
        user = refresh.user
        refresh.delete()
        response = Response({"access": issue_access_token(user)})
        _set_refresh_cookie(response, _issue_refresh(user))
        return response


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

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
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        Profile.objects.create(user=user)
        response = Response({"access": issue_access_token(user)}, status=201)
        _set_refresh_cookie(response, _issue_refresh(user))
        return response


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        return Response(
            {
                "username": request.user.username,
                "email": request.user.email,
                "display_name": profile.display_name,
                "bio": profile.bio,
                "is_leader": profile.is_leader,
            }
        )


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        raw = request.COOKIES.get("pk_refresh")
        if raw:
            RefreshToken.objects.filter(token_hash=hash_token(raw)).delete()
        response = Response(status=204)
        response.delete_cookie("pk_refresh", path="/api/auth", samesite="Lax")
        return response
