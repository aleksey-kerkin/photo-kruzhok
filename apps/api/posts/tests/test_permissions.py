import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from accounts.models import Profile
from posts.api import _can_view_post, _is_leader
from posts.models import Post


@pytest.mark.django_db
def test_is_leader_is_false_without_a_profile():
    user = get_user_model().objects.create_user(
        username="no-profile",
        email="no-profile@example.com",
        password="correct-horse-battery",
    )
    assert _is_leader(user) is False


@pytest.mark.django_db
def test_is_leader_checks_the_profile_flag(member):
    assert _is_leader(AnonymousUser()) is False
    assert _is_leader(member) is False
    member.profile.is_leader = True
    member.profile.save()
    assert _is_leader(member) is True


@pytest.mark.django_db
def test_guest_can_view_visible_posts(member):
    post = Post.objects.create(
        user=member,
        text="visible",
        status=Post.Status.VISIBLE,
    )
    assert _can_view_post(AnonymousUser(), post) is True


@pytest.mark.django_db
def test_guest_cannot_view_hidden_posts(member):
    post = Post.objects.create(
        user=member,
        text="hidden",
        status=Post.Status.HIDDEN,
    )
    assert _can_view_post(AnonymousUser(), post) is False


@pytest.mark.django_db
def test_owner_and_leader_can_view_hidden_posts(member):
    post = Post.objects.create(
        user=member,
        text="hidden",
        status=Post.Status.HIDDEN,
    )
    assert _can_view_post(member, post) is True

    leader = member.__class__.objects.create_user(
        username="leader01",
        email="leader@example.com",
        password="correct-horse-battery",
    )
    Profile.objects.create(user=leader, is_leader=True)
    assert _can_view_post(leader, post) is True
