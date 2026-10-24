import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import NotFound

from posts.api import _get_viewable_post
from posts.models import Post


@pytest.mark.django_db
def test_get_viewable_post_hides_hidden_posts_from_guests(member):
    post = Post.objects.create(
        user=member,
        text="hidden",
        status=Post.Status.HIDDEN,
    )

    with pytest.raises(NotFound):
        _get_viewable_post(AnonymousUser(), post.id)
