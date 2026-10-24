import os

import pytest
from django.core.management import call_command

from posts.models import Post


@pytest.mark.django_db
def test_seed_demo_is_idempotent_for_posts(monkeypatch):
    monkeypatch.setenv("DEMO_MEMBER_PASSWORD", "demo-member-secret")
    monkeypatch.setenv("DEMO_LEADER_PASSWORD", "demo-leader-secret")

    call_command("seed_demo")
    call_command("seed_demo")

    assert Post.objects.count() == 24
