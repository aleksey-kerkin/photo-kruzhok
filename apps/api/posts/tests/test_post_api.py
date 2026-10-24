from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from accounts.access import issue_access_token
from accounts.models import Profile
from posts.models import Post

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
FIXTURE_PATH = FIXTURE_DIR / "sample.jpg"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_jpeg_bytes():
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    if not FIXTURE_PATH.exists():
        image = Image.new("RGB", (64, 48), color=(120, 80, 40))
        image.save(FIXTURE_PATH, format="JPEG")
    return FIXTURE_PATH.read_bytes()


def _auth(user):
    return {"HTTP_AUTHORIZATION": f"Bearer {issue_access_token(user)}"}


def _upload(data: bytes) -> SimpleUploadedFile:
    return SimpleUploadedFile("sample.jpg", data, content_type="image/jpeg")


@pytest.mark.django_db
def test_guest_lists_only_visible_posts(api_client, member, sample_jpeg_bytes):
    visible = Post.objects.create(user=member, text="visible one")
    Post.objects.create(user=member, text="hidden one", status=Post.Status.HIDDEN)

    response = api_client.get("/api/posts")

    assert response.status_code == 200
    body = response.json()
    assert "results" in body
    assert "next_cursor" in body
    assert "has_next" in body
    ids = [item["id"] for item in body["results"]]
    assert visible.id in ids
    assert len(ids) == 1


@pytest.mark.django_db
def test_member_creates_post_with_image(api_client, member, sample_jpeg_bytes):
    response = api_client.post(
        "/api/posts",
        {"caption": "Morning light", "image": _upload(sample_jpeg_bytes)},
        **_auth(member),
        format="multipart",
    )

    assert response.status_code == 201
    body = response.json()
    assert body["caption"] == "Morning light"
    assert body["width"] == 64
    assert body["height"] == 48
    assert body["status"] == "visible"
    assert body["likes_count"] == 0
    assert body["liked_by_me"] is False
    assert Post.objects.filter(user=member, text="Morning light").exists()


@pytest.mark.django_db
def test_create_post_rejects_caption_over_2000_chars(api_client, member, sample_jpeg_bytes):
    response = api_client.post(
        "/api/posts",
        {"caption": "x" * 2001, "image": _upload(sample_jpeg_bytes)},
        **_auth(member),
        format="multipart",
    )

    assert response.status_code == 400
    assert response.json()["code"] == "validation_error"
    assert "caption" in response.json()["fields"]


@pytest.mark.django_db
def test_member_patches_caption_only(api_client, member, sample_jpeg_bytes):
    create = api_client.post(
        "/api/posts",
        {"caption": "Before", "image": _upload(sample_jpeg_bytes)},
        **_auth(member),
        format="multipart",
    )
    post_id = create.json()["id"]

    response = api_client.patch(
        f"/api/posts/{post_id}",
        {"caption": "After"},
        **_auth(member),
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["caption"] == "After"
    post = Post.objects.get(pk=post_id)
    assert post.text == "After"
    assert post.status == Post.Status.VISIBLE


@pytest.mark.django_db
def test_owner_deletes_post(api_client, member, sample_jpeg_bytes):
    create = api_client.post(
        "/api/posts",
        {"caption": "Delete me", "image": _upload(sample_jpeg_bytes)},
        **_auth(member),
        format="multipart",
    )
    post_id = create.json()["id"]

    response = api_client.delete(f"/api/posts/{post_id}", **_auth(member))

    assert response.status_code == 204
    assert not Post.objects.filter(pk=post_id).exists()


@pytest.fixture
def leader(db):
    user = get_user_model().objects.create_user(
        username="leader01",
        email="leader@example.com",
        password="correct-horse-battery",
    )
    Profile.objects.create(user=user, is_leader=True)
    return user


@pytest.mark.django_db
def test_leader_hides_post_and_lists_hidden(
    api_client, member, leader, sample_jpeg_bytes
):
    create = api_client.post(
        "/api/posts",
        {"caption": "To hide", "image": _upload(sample_jpeg_bytes)},
        **_auth(member),
        format="multipart",
    )
    post_id = create.json()["id"]

    hide = api_client.post(f"/api/posts/{post_id}/hide", **_auth(leader))
    assert hide.status_code == 200
    assert hide.json()["status"] == "hidden"

    hidden_list = api_client.get("/api/posts?status=hidden", **_auth(leader))
    assert hidden_list.status_code == 200
    ids = [item["id"] for item in hidden_list.json()["results"]]
    assert post_id in ids


@pytest.mark.django_db
def test_non_author_member_gets_404_after_leader_hides(
    api_client, member, leader, sample_jpeg_bytes
):
    other = get_user_model().objects.create_user(
        username="boris03",
        email="boris03@example.com",
        password="correct-horse-battery",
    )
    Profile.objects.create(user=other)

    create = api_client.post(
        "/api/posts",
        {"caption": "Secret", "image": _upload(sample_jpeg_bytes)},
        **_auth(member),
        format="multipart",
    )
    post_id = create.json()["id"]
    api_client.post(f"/api/posts/{post_id}/hide", **_auth(leader))

    response = api_client.get(f"/api/posts/{post_id}", **_auth(other))
    assert response.status_code == 404


@pytest.mark.django_db
def test_non_leader_hide_returns_403(api_client, member, sample_jpeg_bytes):
    create = api_client.post(
        "/api/posts",
        {"caption": "No hide", "image": _upload(sample_jpeg_bytes)},
        **_auth(member),
        format="multipart",
    )
    post_id = create.json()["id"]

    response = api_client.post(f"/api/posts/{post_id}/hide", **_auth(member))
    assert response.status_code == 403


@pytest.mark.django_db
def test_leader_restores_post_guest_sees_it_again(
    api_client, member, leader, sample_jpeg_bytes
):
    create = api_client.post(
        "/api/posts",
        {"caption": "Restore me", "image": _upload(sample_jpeg_bytes)},
        **_auth(member),
        format="multipart",
    )
    post_id = create.json()["id"]
    api_client.post(f"/api/posts/{post_id}/hide", **_auth(leader))

    restore = api_client.post(f"/api/posts/{post_id}/restore", **_auth(leader))
    assert restore.status_code == 200
    assert restore.json()["status"] == "visible"

    guest_list = api_client.get("/api/posts")
    assert guest_list.status_code == 200
    ids = [item["id"] for item in guest_list.json()["results"]]
    assert post_id in ids


@pytest.mark.django_db
def test_stranger_gets_404_for_hidden_post(api_client, member, sample_jpeg_bytes):
    other = get_user_model().objects.create_user(
        username="boris02",
        email="boris@example.com",
        password="correct-horse-battery",
    )
    Profile.objects.create(user=other)

    hidden = Post.objects.create(
        user=member,
        text="secret",
        status=Post.Status.HIDDEN,
        content_hash="deadbeef",
        width=10,
        height=10,
    )

    response = api_client.get(f"/api/posts/{hidden.id}", **_auth(other))

    assert response.status_code == 404
