import pytest
from rest_framework.test import APIClient

from accounts.access import issue_access_token
from posts.models import Comment, Post


@pytest.fixture
def api_client():
    return APIClient()


def _auth(user):
    return {"HTTP_AUTHORIZATION": f"Bearer {issue_access_token(user)}"}


@pytest.mark.django_db
def test_reply_to_reply_is_returned_under_root(api_client, member):
    post = Post.objects.create(user=member, text="photo")

    root_resp = api_client.post(
        f"/api/posts/{post.id}/comments",
        {"text": "root"},
        **_auth(member),
        format="json",
    )
    assert root_resp.status_code == 201
    root_id = root_resp.json()["id"]

    reply_resp = api_client.post(
        f"/api/posts/{post.id}/comments",
        {"text": "reply", "parent_id": root_id},
        **_auth(member),
        format="json",
    )
    assert reply_resp.status_code == 201
    reply_id = reply_resp.json()["id"]

    nested_resp = api_client.post(
        f"/api/posts/{post.id}/comments",
        {"text": "nested", "parent_id": reply_id},
        **_auth(member),
        format="json",
    )
    assert nested_resp.status_code == 201
    nested_id = nested_resp.json()["id"]

    stored = Comment.objects.get(pk=nested_id)
    assert stored.parent_id == root_id

    list_resp = api_client.get(f"/api/posts/{post.id}/comments")
    assert list_resp.status_code == 200
    body = list_resp.json()
    assert len(body["results"]) == 1
    root_item = body["results"][0]
    assert root_item["id"] == root_id
    reply_texts = {item["text"] for item in root_item["replies"]}
    assert reply_texts == {"reply", "nested"}
