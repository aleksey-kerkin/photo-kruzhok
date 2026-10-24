import pytest
from django.core.files.storage import default_storage
from django.test import RequestFactory

from posts.api import _derivative_payload, _iso_z, _save_derivatives
from posts.models import Post


@pytest.mark.django_db
def test_save_derivatives_and_payload(member):
    post = Post.objects.create(user=member, text="Derivatives")
    _save_derivatives(post, {"webp": {480: b"webp-bytes"}})

    path = f"posts/derivatives/{post.id}/webp_480.webp"
    assert default_storage.exists(path)

    request = RequestFactory().get("/")
    payload = _derivative_payload(post, request)
    assert payload[0]["format"] == "webp"
    assert payload[0]["width"] == 480
    assert _iso_z(post.created_at).endswith("Z")


@pytest.mark.django_db
def test_annotate_posts_for_guests_does_not_add_liked_by_me(member):
    from django.contrib.auth.models import AnonymousUser

    from posts.api import _annotate_posts_with_likes

    Post.objects.create(user=member, text="Guest list")
    queryset = _annotate_posts_with_likes(Post.objects.all(), AnonymousUser())
    assert "liked_by_me" not in queryset.query.annotations

    member_queryset = _annotate_posts_with_likes(Post.objects.all(), member)
    assert "liked_by_me" in member_queryset.query.annotations
