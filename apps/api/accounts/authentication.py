from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication

from accounts.access import read_access_token

User = get_user_model()


class AccessTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header.startswith("Bearer "):
            return None
        raw = header[7:].strip()
        if not raw:
            return None
        try:
            payload = read_access_token(raw)
        except Exception:
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        return (user, payload)

    def authenticate_header(self, request):
        return "Bearer"
