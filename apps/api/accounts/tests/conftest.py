import pytest
from django.contrib.auth import get_user_model

from accounts.models import Profile


@pytest.fixture
def member(db):
    user = get_user_model().objects.create_user(
        username="anya01",
        email="anya@example.com",
        password="correct-horse-battery",
    )
    Profile.objects.create(user=user)
    return user
