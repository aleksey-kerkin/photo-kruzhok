import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from posts.models import Post
from posts.views import PostCreateView, PostListView


@pytest.mark.django_db
def test_post_list_view_renders_posts():
    user = get_user_model().objects.create_user(
        username="list-user",
        email="list@example.com",
        password="correct-horse-battery",
    )
    Post.objects.create(user=user, text="List caption", status=Post.Status.VISIBLE)

    request = RequestFactory().get("/posts/")
    request.user = user
    response = PostListView.as_view()(request)
    response.render()

    assert response.status_code == 200
    assert b"List caption" in response.content


@pytest.mark.django_db
def test_post_create_view_assigns_the_current_user(member):
    request = RequestFactory().post(
        "/posts/create/",
        data={"text": "Created caption"},
    )
    request.user = member
    response = PostCreateView.as_view()(request)

    assert response.status_code in {200, 302}
    assert Post.objects.filter(user=member, text="Created caption").exists()
