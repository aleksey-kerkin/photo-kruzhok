from datetime import timedelta
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from PIL import Image
from rest_framework.test import APIClient

from accounts.access import issue_access_token
from accounts.models import Profile
from challenges.models import Challenge, Submission, Vote
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


def _upload(data: bytes) -> SimpleUploadedFile:
    return SimpleUploadedFile("sample.jpg", data, content_type="image/jpeg")


def _challenge_payload(**overrides):
    now = timezone.now()
    payload = {
        "title": "Golden hour",
        "description": "Shoot at sunset",
        "start": (now + timedelta(days=1)).isoformat().replace("+00:00", "Z"),
        "end": (now + timedelta(days=8)).isoformat().replace("+00:00", "Z"),
    }
    payload.update(overrides)
    return payload


def _open_challenge(leader, **overrides):
    user_model = get_user_model()
    if not isinstance(leader, user_model):
        raise TypeError("leader must be a user")
    client = APIClient()
    response = client.post(
        "/api/challenges",
        _challenge_payload(**overrides),
        **_auth(leader),
        format="json",
    )
    assert response.status_code == 201
    return response.json()


def _member_post(client, member, sample_jpeg_bytes, caption="entry", color=(120, 80, 40)):
    image = Image.new("RGB", (64, 48), color=color)
    from io import BytesIO

    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    data = buffer.getvalue()
    response = client.post(
        "/api/posts",
        {
            "caption": caption,
            "image": SimpleUploadedFile("sample.jpg", data, content_type="image/jpeg"),
        },
        **_auth(member),
        format="multipart",
    )
    assert response.status_code == 201
    return response.json()["id"]


@pytest.mark.django_db
def test_get_challenges_current_returns_open_theme(api_client, leader):
    opened = _open_challenge(leader)

    response = api_client.get("/api/challenges/current")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == opened["id"]
    assert body["status"] == "open"


@pytest.mark.django_db
def test_get_challenge_by_id(api_client, leader):
    opened = _open_challenge(leader)

    response = api_client.get(f"/api/challenges/{opened['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "Golden hour"


@pytest.mark.django_db
def test_post_challenges_opens_theme(api_client, leader):
    response = api_client.post(
        "/api/challenges",
        _challenge_payload(),
        **_auth(leader),
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["status"] == "open"
    assert Challenge.objects.filter(status=Challenge.Status.OPEN).count() == 1


@pytest.mark.django_db
def test_post_challenges_draft_does_not_open(api_client, leader):
    response = api_client.post(
        "/api/challenges",
        {**_challenge_payload(), "status": "draft"},
        **_auth(leader),
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["status"] == "draft"
    assert Challenge.objects.filter(status=Challenge.Status.OPEN).count() == 0
    assert api_client.get("/api/challenges/current").status_code == 404


@pytest.mark.django_db
def test_second_open_challenge_returns_409(api_client, leader):
    _open_challenge(leader)

    response = api_client.post(
        "/api/challenges",
        _challenge_payload(title="Another"),
        **_auth(leader),
        format="json",
    )

    assert response.status_code == 409


@pytest.mark.django_db
def test_patch_challenge(api_client, leader):
    opened = _open_challenge(leader)

    response = api_client.patch(
        f"/api/challenges/{opened['id']}",
        {"title": "Updated title"},
        **_auth(leader),
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"


@pytest.mark.django_db
def test_close_challenge(api_client, leader):
    opened = _open_challenge(leader)

    response = api_client.post(f"/api/challenges/{opened['id']}/close", **_auth(leader))

    assert response.status_code == 200
    assert response.json()["status"] == "closed"
    assert api_client.get("/api/challenges/current").status_code == 404


@pytest.mark.django_db
def test_list_and_create_submission(api_client, member, leader, sample_jpeg_bytes):
    opened = _open_challenge(leader)
    post_id = _member_post(api_client, member, sample_jpeg_bytes)

    create = api_client.post(
        f"/api/challenges/{opened['id']}/submissions",
        {"post_id": post_id},
        **_auth(member),
        format="json",
    )
    assert create.status_code == 201
    submission_id = create.json()["id"]

    listing = api_client.get(f"/api/challenges/{opened['id']}/submissions")
    assert listing.status_code == 200
    ids = [item["id"] for item in listing.json()["results"]]
    assert ids == [submission_id]


@pytest.mark.django_db
def test_second_submission_from_same_member_returns_409(
    api_client, member, leader, sample_jpeg_bytes
):
    opened = _open_challenge(leader)
    first_post = _member_post(api_client, member, sample_jpeg_bytes, caption="one")
    second_post = _member_post(
        api_client, member, sample_jpeg_bytes, caption="two", color=(40, 80, 120)
    )
    api_client.post(
        f"/api/challenges/{opened['id']}/submissions",
        {"post_id": first_post},
        **_auth(member),
        format="json",
    )

    response = api_client.post(
        f"/api/challenges/{opened['id']}/submissions",
        {"post_id": second_post},
        **_auth(member),
        format="json",
    )

    assert response.status_code == 409


@pytest.mark.django_db
def test_withdraw_submission_deletes_votes(
    api_client, member, leader, sample_jpeg_bytes
):
    other = get_user_model().objects.create_user(
        username="boris03",
        email="boris03@example.com",
        password="correct-horse-battery",
    )
    Profile.objects.create(user=other)
    opened = _open_challenge(leader)
    post_id = _member_post(api_client, member, sample_jpeg_bytes)
    submission = api_client.post(
        f"/api/challenges/{opened['id']}/submissions",
        {"post_id": post_id},
        **_auth(member),
        format="json",
    ).json()
    api_client.post(
        f"/api/challenges/{opened['id']}/votes",
        {"submission_id": submission["id"]},
        **_auth(other),
        format="json",
    )
    assert Vote.objects.filter(submission_id=submission["id"]).count() == 1

    response = api_client.delete(
        f"/api/challenges/{opened['id']}/submissions/{submission['id']}",
        **_auth(member),
    )

    assert response.status_code == 204
    assert not Submission.objects.filter(pk=submission["id"]).exists()
    assert Vote.objects.filter(submission_id=submission["id"]).count() == 0


@pytest.mark.django_db
def test_vote_sets_and_replaces(api_client, member, leader, sample_jpeg_bytes):
    other = get_user_model().objects.create_user(
        username="carl04",
        email="carl04@example.com",
        password="correct-horse-battery",
    )
    Profile.objects.create(user=other)
    opened = _open_challenge(leader)
    post_a = _member_post(api_client, member, sample_jpeg_bytes, caption="a")
    post_b = _member_post(api_client, other, sample_jpeg_bytes, caption="b")
    sub_a = api_client.post(
        f"/api/challenges/{opened['id']}/submissions",
        {"post_id": post_a},
        **_auth(member),
        format="json",
    ).json()
    sub_b = api_client.post(
        f"/api/challenges/{opened['id']}/submissions",
        {"post_id": post_b},
        **_auth(other),
        format="json",
    ).json()

    voter = get_user_model().objects.create_user(
        username="dora05",
        email="dora05@example.com",
        password="correct-horse-battery",
    )
    Profile.objects.create(user=voter)

    first = api_client.post(
        f"/api/challenges/{opened['id']}/votes",
        {"submission_id": sub_a["id"]},
        **_auth(voter),
        format="json",
    )
    assert first.status_code == 200
    vote = Vote.objects.get(user=voter, challenge_id=opened["id"])
    assert vote.submission_id == sub_a["id"]

    second = api_client.post(
        f"/api/challenges/{opened['id']}/votes",
        {"submission_id": sub_b["id"]},
        **_auth(voter),
        format="json",
    )
    assert second.status_code == 200
    vote.refresh_from_db()
    assert vote.submission_id == sub_b["id"]
    assert Vote.objects.filter(user=voter, challenge_id=opened["id"]).count() == 1


@pytest.mark.django_db
def test_stats_leader_only(api_client, member, leader, sample_jpeg_bytes):
    opened = _open_challenge(leader)
    post_id = _member_post(api_client, member, sample_jpeg_bytes)
    submission = api_client.post(
        f"/api/challenges/{opened['id']}/submissions",
        {"post_id": post_id},
        **_auth(member),
        format="json",
    ).json()
    api_client.post(
        f"/api/challenges/{opened['id']}/votes",
        {"submission_id": submission["id"]},
        **_auth(leader),
        format="json",
    )

    denied = api_client.get(f"/api/challenges/{opened['id']}/stats", **_auth(member))
    assert denied.status_code == 403

    stats = api_client.get(f"/api/challenges/{opened['id']}/stats", **_auth(leader))
    assert stats.status_code == 200
    body = stats.json()
    assert body == {
        "submissions_count": 1,
        "votes_count": 1,
        "participants_count": 2,
    }


@pytest.mark.django_db
def test_hidden_submission_excluded_for_guests_marked_for_leader(
    api_client, member, leader, sample_jpeg_bytes
):
    opened = _open_challenge(leader)
    post_id = _member_post(api_client, member, sample_jpeg_bytes)
    submission = api_client.post(
        f"/api/challenges/{opened['id']}/submissions",
        {"post_id": post_id},
        **_auth(member),
        format="json",
    ).json()
    api_client.post(f"/api/posts/{post_id}/hide", **_auth(leader))

    guest_list = api_client.get(f"/api/challenges/{opened['id']}/submissions")
    assert guest_list.status_code == 200
    assert guest_list.json()["results"] == []

    leader_list = api_client.get(
        f"/api/challenges/{opened['id']}/submissions", **_auth(leader)
    )
    assert leader_list.status_code == 200
    results = leader_list.json()["results"]
    assert len(results) == 1
    assert results[0]["id"] == submission["id"]
    assert results[0]["hidden"] is True
    assert Submission.objects.filter(pk=submission["id"]).exists()
