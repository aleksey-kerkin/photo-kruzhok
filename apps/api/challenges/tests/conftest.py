import pytest
from django.contrib.auth import get_user_model

from accounts.models import Profile


@pytest.fixture
def leader(db):
    user = get_user_model().objects.create_user(
        username="leader01",
        email="leader@example.com",
        password="correct-horse-battery",
    )
    Profile.objects.create(user=user, is_leader=True)
    return user
