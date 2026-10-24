from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from rest_framework.test import APIClient

from accounts.access import issue_access_token
from accounts.models import Profile
from posts.models import Post

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "posts" / "tests" / "fixtures"
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


@pytest.mark.django_db
def test_get_profile_by_username(api_client, member):
    member.profile.display_name = "Anya"
    member.profile.bio = "Street photos"
    member.profile.save()

    response = api_client.get("/api/profiles/anya01")

    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "anya01"
    assert body["display_name"] == "Anya"
    assert body["bio"] == "Street photos"
    assert body["avatar"] is None


@pytest.mark.django_db
def test_empty_display_name_falls_back_to_username(api_client, member):
    response = api_client.get("/api/profiles/anya01")

    assert response.status_code == 200
    assert response.json()["display_name"] == "anya01"


@pytest.mark.django_db
def test_patch_profile_me_updates_fields(api_client, member, sample_jpeg_bytes):
    avatar = SimpleUploadedFile("avatar.jpg", sample_jpeg_bytes, content_type="image/jpeg")

    response = api_client.patch(
        "/api/profiles/me",
        {
            "display_name": "Anya K.",
            "bio": "Light hunter",
            "avatar": avatar,
        },
        **_auth(member),
        format="multipart",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["display_name"] == "Anya K."
    assert body["bio"] == "Light hunter"
    assert body["avatar"] is not None
    member.profile.refresh_from_db()
    assert member.profile.display_name == "Anya K."
    assert member.profile.bio == "Light hunter"
    assert member.profile.avatar


@pytest.mark.django_db
def test_profile_posts_use_cursor_and_show_visible_only(api_client, member, sample_jpeg_bytes):
    visible = Post.objects.create(
        user=member,
        text="on profile",
        width=64,
        height=48,
        content_hash="hash-visible",
    )
    Post.objects.create(
        user=member,
        text="hidden",
        status=Post.Status.HIDDEN,
        width=64,
        height=48,
        content_hash="hash-hidden",
    )

    response = api_client.get("/api/profiles/anya01/posts")

    assert response.status_code == 200
    body = response.json()
    assert "results" in body
    assert "next_cursor" in body
    assert "has_next" in body
    ids = [item["id"] for item in body["results"]]
    assert ids == [visible.id]
