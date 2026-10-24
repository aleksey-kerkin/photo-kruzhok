import pytest
from django.contrib.auth import get_user_model

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
