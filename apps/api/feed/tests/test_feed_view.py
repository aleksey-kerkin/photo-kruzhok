import pytest
from django.test import RequestFactory

from feed.views import feed
from posts.models import Post


@pytest.mark.django_db
def test_feed_view_lists_posts_for_signed_in_user(member):
    Post.objects.create(user=member, text="Feed caption", status=Post.Status.VISIBLE)

    request = RequestFactory().get("/posts/")
    request.user = member
    response = feed(request)

    assert response.status_code == 200
    assert b"Feed caption" in response.content
