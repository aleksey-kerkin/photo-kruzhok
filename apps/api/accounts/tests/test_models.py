from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.hashes import hash_token
from accounts.models import Profile, RefreshToken


@pytest.mark.django_db
def test_profile_defaults_and_token_stores_only_a_hash():
    user = get_user_model().objects.create_user(
        username="anya01",
        email="anya@example.com",
        password="correct-horse-battery",
    )
    profile = Profile.objects.create(user=user)
    assert profile.is_leader is False
    assert profile.display_name == ""
    raw = "refresh-token-value"
    stored = RefreshToken.objects.create(
        user=user,
        token_hash=hash_token(raw),
        expires_at=timezone.now() + timedelta(days=7),
    )
    assert stored.token_hash == hash_token(raw)
    assert raw not in stored.token_hash
