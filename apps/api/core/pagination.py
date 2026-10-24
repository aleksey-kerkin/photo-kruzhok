import base64
from datetime import datetime

from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime


class CursorPagination:
    default_limit = 20
    max_limit = 50

    def paginate(self, queryset, request):
        limit = self._get_limit(request)
        cursor = self._get_cursor(request)

        qs = queryset.order_by("-created_at", "-id")
        if cursor:
            created_at, row_id = _decode_cursor(cursor)
            qs = qs.filter(
                Q(created_at__lt=created_at)
                | Q(created_at=created_at, id__lt=row_id)
            )

        rows = list(qs[: limit + 1])
        has_next = len(rows) > limit
        results = rows[:limit]

        next_cursor = None
        if has_next and results:
            last = results[-1]
            next_cursor = _encode_cursor(last.created_at, last.id)

        return {
            "results": results,
            "next_cursor": next_cursor,
            "has_next": has_next,
        }

    def _get_query_params(self, request):
        return getattr(request, "query_params", request.GET)

    def _get_limit(self, request):
        params = self._get_query_params(request)
        raw = params.get("limit", str(self.default_limit))
        try:
            limit = int(raw)
        except (TypeError, ValueError):
            limit = self.default_limit
        if limit < 1:
            limit = self.default_limit
        return min(limit, self.max_limit)

    def _get_cursor(self, request):
        params = self._get_query_params(request)
        return params.get("cursor") or None


def _encode_cursor(created_at: datetime, row_id: int) -> str:
    if timezone.is_naive(created_at):
        created_at = timezone.make_aware(created_at, timezone.utc)
    payload = f"{created_at.isoformat()}|{row_id}"
    return base64.urlsafe_b64encode(payload.encode()).decode()


def _decode_cursor(cursor: str) -> tuple[datetime, int]:
    try:
        payload = base64.urlsafe_b64decode(cursor.encode()).decode()
        created_at_str, row_id_str = payload.split("|", 1)
        created_at = parse_datetime(created_at_str)
        if created_at is None:
            raise ValueError("invalid datetime in cursor")
        if timezone.is_naive(created_at):
            created_at = timezone.make_aware(created_at, timezone.utc)
        return created_at, int(row_id_str)
    except (ValueError, TypeError, UnicodeDecodeError):
        raise ValueError("invalid cursor")
