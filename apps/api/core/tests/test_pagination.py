from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.utils import timezone

from core.pagination import CursorPagination
from posts.models import Post


@pytest.mark.django_db
def test_cursor_pagination_returns_remaining_row_on_second_page():
    user = get_user_model().objects.create_user(
        "paginator01", "pag@example.com", "correct-horse-battery"
    )
    base = timezone.now()
    posts = []
    for i in range(3):
        post = Post.objects.create(user=user, content_hash=f"hash-{i}")
        Post.objects.filter(pk=post.pk).update(
            created_at=base + timedelta(seconds=i)
        )
        posts.append(Post.objects.get(pk=post.pk))

    ordered = sorted(posts, key=lambda p: (-p.created_at.timestamp(), -p.id))
    paginator = CursorPagination()
    factory = RequestFactory()

    first_request = factory.get("/", {"limit": "2"})
    first_page = paginator.paginate(Post.objects.all(), first_request)

    assert first_page["has_next"] is True
    assert first_page["next_cursor"]
    assert [item.id for item in first_page["results"]] == [
        ordered[0].id,
        ordered[1].id,
    ]

    second_request = factory.get(
        "/",
        {"limit": "2", "cursor": first_page["next_cursor"]},
    )
    second_page = paginator.paginate(Post.objects.all(), second_request)

    assert second_page["has_next"] is False
    assert [item.id for item in second_page["results"]] == [ordered[2].id]
