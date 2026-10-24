from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from challenges.models import Challenge, Submission, Vote
from core.pagination import CursorPagination
from posts.api import Conflict, _get_viewable_post, _is_leader, serialize_post
from posts.models import Post


def _iso_z(dt) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _require_leader(user):
    if not _is_leader(user):
        raise PermissionDenied()


def _serialize_challenge(challenge: Challenge) -> dict:
    return {
        "id": challenge.id,
        "title": challenge.title,
        "description": challenge.description,
        "start": _iso_z(challenge.start),
        "end": _iso_z(challenge.end),
        "status": challenge.status,
        "created_at": _iso_z(challenge.created_at),
        "updated_at": _iso_z(challenge.updated_at),
    }


def _parse_datetime_field(value, field_name: str):
    if value is None:
        raise ValidationError({field_name: ["This field is required."]})
    if isinstance(value, str):
        parsed = parse_datetime(value.replace("Z", "+00:00"))
        if parsed is None:
            raise ValidationError({field_name: ["Enter a valid date/time."]})
        return parsed
    raise ValidationError({field_name: ["Enter a valid date/time."]})


def _submission_visible_to_caller(submission: Submission, user) -> bool:
    if submission.post.status == Post.Status.VISIBLE:
        return True
    return _is_leader(user)


def _submissions_queryset(challenge: Challenge, user):
    qs = Submission.objects.filter(challenge=challenge).select_related("post", "post__user")
    if _is_leader(user):
        return qs
    return qs.filter(post__status=Post.Status.VISIBLE)


def _serialize_submission(submission: Submission, request) -> dict:
    hidden = submission.post.status == Post.Status.HIDDEN
    payload = {
        "id": submission.id,
        "post": serialize_post(submission.post, request),
        "created_at": _iso_z(submission.created_at),
    }
    if hidden:
        payload["hidden"] = True
    return payload


def _visible_submissions_qs(challenge: Challenge):
    return Submission.objects.filter(
        challenge=challenge,
        post__status=Post.Status.VISIBLE,
    )


def _included_votes_qs(challenge: Challenge):
    return Vote.objects.filter(
        challenge=challenge,
        submission__post__status=Post.Status.VISIBLE,
    )


class ChallengeCurrentView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        challenge = Challenge.objects.filter(status=Challenge.Status.OPEN).first()
        if challenge is None:
            raise NotFound()
        return Response(_serialize_challenge(challenge))


class ChallengeDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, pk):
        challenge = get_object_or_404(Challenge, pk=pk)
        return Response(_serialize_challenge(challenge))

    def patch(self, request, pk):
        _require_leader(request.user)
        challenge = get_object_or_404(Challenge, pk=pk)
        if "title" in request.data:
            challenge.title = str(request.data["title"])
        if "description" in request.data:
            challenge.description = str(request.data.get("description") or "")
        if "start" in request.data:
            challenge.start = _parse_datetime_field(request.data["start"], "start")
        if "end" in request.data:
            challenge.end = _parse_datetime_field(request.data["end"], "end")
        challenge.save()
        return Response(_serialize_challenge(challenge))


class ChallengeListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        _require_leader(request.user)
        title = request.data.get("title")
        if not title:
            raise ValidationError({"title": ["This field is required."]})
        description = str(request.data.get("description") or "")
        start = _parse_datetime_field(request.data.get("start"), "start")
        end = _parse_datetime_field(request.data.get("end"), "end")
        status = request.data.get("status", Challenge.Status.OPEN)
        if status not in Challenge.Status.values:
            raise ValidationError({"status": ["Invalid status."]})
        if status == Challenge.Status.OPEN:
            if Challenge.objects.filter(status=Challenge.Status.OPEN).exists():
                raise Conflict()
        challenge = Challenge.objects.create(
            title=str(title),
            description=description,
            start=start,
            end=end,
            status=status,
            created_by=request.user,
        )
        return Response(_serialize_challenge(challenge), status=201)


class ChallengeCloseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        _require_leader(request.user)
        challenge = get_object_or_404(Challenge, pk=pk)
        challenge.status = Challenge.Status.CLOSED
        challenge.save(update_fields=["status", "updated_at"])
        return Response(_serialize_challenge(challenge))


class ChallengeSubmissionListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, pk):
        challenge = get_object_or_404(Challenge, pk=pk)
        qs = _submissions_queryset(challenge, request.user)
        page = CursorPagination().paginate(qs, request)
        page["results"] = [
            _serialize_submission(submission, request) for submission in page["results"]
        ]
        return Response(page)

    def post(self, request, pk):
        challenge = get_object_or_404(Challenge, pk=pk)
        if challenge.status != Challenge.Status.OPEN:
            raise ValidationError({"challenge": ["Submissions are only allowed on open themes."]})
        post_id = request.data.get("post_id")
        if post_id is None:
            raise ValidationError({"post_id": ["This field is required."]})
        try:
            post_id = int(post_id)
        except (TypeError, ValueError):
            raise ValidationError({"post_id": ["A valid integer is required."]})
        post = _get_viewable_post(request.user, post_id)
        if post.user_id != request.user.id:
            raise PermissionDenied()
        if Submission.objects.filter(challenge=challenge, post__user=request.user).exists():
            raise Conflict()
        submission = Submission.objects.create(challenge=challenge, post=post)
        return Response(_serialize_submission(submission, request), status=201)


class ChallengeSubmissionWithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, submission_id):
        challenge = get_object_or_404(Challenge, pk=pk)
        submission = get_object_or_404(
            Submission,
            pk=submission_id,
            challenge=challenge,
        )
        if submission.post.user_id != request.user.id:
            raise PermissionDenied()
        submission.delete()
        return Response(status=204)


class ChallengeVoteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        challenge = get_object_or_404(Challenge, pk=pk)
        if challenge.status != Challenge.Status.OPEN:
            raise ValidationError({"challenge": ["Votes are only allowed on open themes."]})
        submission_id = request.data.get("submission_id")
        if submission_id is None:
            raise ValidationError({"submission_id": ["This field is required."]})
        try:
            submission_id = int(submission_id)
        except (TypeError, ValueError):
            raise ValidationError({"submission_id": ["A valid integer is required."]})
        submission = get_object_or_404(
            Submission,
            pk=submission_id,
            challenge=challenge,
        )
        if not _submission_visible_to_caller(submission, request.user):
            raise NotFound()
        vote, _created = Vote.objects.update_or_create(
            user=request.user,
            challenge=challenge,
            defaults={"submission": submission},
        )
        return Response(
            {
                "submission_id": vote.submission_id,
                "challenge_id": challenge.id,
            }
        )


class ChallengeStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        _require_leader(request.user)
        challenge = get_object_or_404(Challenge, pk=pk)
        submissions_count = _visible_submissions_qs(challenge).count()
        votes_count = _included_votes_qs(challenge).count()
        submission_authors = _visible_submissions_qs(challenge).values_list(
            "post__user_id", flat=True
        )
        vote_authors = _included_votes_qs(challenge).values_list("user_id", flat=True)
        participants_count = len(set(submission_authors) | set(vote_authors))
        return Response(
            {
                "submissions_count": submissions_count,
                "votes_count": votes_count,
                "participants_count": participants_count,
            }
        )
