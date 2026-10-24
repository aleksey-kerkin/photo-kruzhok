import pytest
from django.contrib.auth import get_user_model
from django.urls import NoReverseMatch

from posts.models import Post


@pytest.mark.django_db
def test_post_defaults_to_visible_without_gps_fields():
    user = get_user_model().objects.create_user(
        "anya01", "anya@example.com", "correct-horse-battery"
    )
    post = Post.objects.create(user=user, content_hash="abc", width=100, height=50)
    assert post.status == "visible"
    assert post.exif == {}
    assert "gps" not in post.exif


@pytest.mark.django_db
def test_post_string_representation_mentions_the_author():
    user = get_user_model().objects.create_user(
        "slug-user", "slug@example.com", "correct-horse-battery"
    )
    post = Post.objects.create(user=user, text="Slug caption")
    assert "slug-user" in str(post)


@pytest.mark.django_db
def test_post_absolute_url_uses_the_post_detail_route(member):
    post = Post.objects.create(user=member, text="Caption")
    with pytest.raises(NoReverseMatch):
        post.get_absolute_url()
