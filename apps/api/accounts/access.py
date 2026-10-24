from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings


def issue_access_token(user) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user.id), "iat": now, "exp": now + timedelta(minutes=15)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def read_access_token(raw: str) -> dict:
    return jwt.decode(raw, settings.SECRET_KEY, algorithms=["HS256"])
