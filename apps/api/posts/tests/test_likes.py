import pytest
from rest_framework.test import APIClient

from accounts.access import issue_access_token
from posts.models import Post


@pytest.fixture
def api_client():
    return APIClient()


def _auth(user):
    return {"HTTP_AUTHORIZATION": f"Bearer {issue_access_token(user)}"}


@pytest.mark.django_db
def test_like_then_unlike_sets_liked_by_me_false(api_client, member):
    post = Post.objects.create(user=member, text="photo")

    like_resp = api_client.put(f"/api/posts/{post.id}/like", **_auth(member))
    assert like_resp.status_code == 200

    after_like = api_client.get(f"/api/posts/{post.id}", **_auth(member))
    assert after_like.status_code == 200
    assert after_like.json()["liked_by_me"] is True
    assert after_like.json()["likes_count"] == 1

    unlike_resp = api_client.delete(f"/api/posts/{post.id}/like", **_auth(member))
    assert unlike_resp.status_code == 200

    after_unlike = api_client.get(f"/api/posts/{post.id}", **_auth(member))
    assert after_unlike.status_code == 200
    assert after_unlike.json()["liked_by_me"] is False
    assert after_unlike.json()["likes_count"] == 0
