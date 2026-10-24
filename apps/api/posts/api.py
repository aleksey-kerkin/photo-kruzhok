from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Count, Exists, OuterRef, Q
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from rest_framework.exceptions import APIException, NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.pagination import CursorPagination
from posts.images import DERIVATIVE_WIDTHS
from posts.models import Comment, Like, Post


class Conflict(APIException):
    status_code = 409
    default_detail = "Conflict."


def _is_leader(user) -> bool:
    if not user.is_authenticated:
        return False
    profile = getattr(user, "profile", None)
    return profile is not None and profile.is_leader


def _can_view_post(user, post: Post) -> bool:
    if post.status == Post.Status.VISIBLE:
        return True
    if not user.is_authenticated:
        return False
    if post.user_id == user.id:
        return True
    return _is_leader(user)


def _get_viewable_post(user, post_id: int) -> Post:
    post = get_object_or_404(Post, pk=post_id)
    if not _can_view_post(user, post):
        raise NotFound()
    return post


def _save_derivatives(post: Post, files: dict) -> None:
    for fmt, widths in files.items():
        ext = fmt
        for width, data in widths.items():
            path = f"posts/derivatives/{post.id}/{fmt}_{width}.{ext}"
            default_storage.save(path, ContentFile(data))


def _derivative_payload(post: Post, request) -> list[dict]:
    items = []
    for fmt in ("webp", "avif"):
        for width in DERIVATIVE_WIDTHS:
            path = f"posts/derivatives/{post.id}/{fmt}_{width}.{fmt}"
            if default_storage.exists(path):
                items.append(
                    {
                        "format": fmt,
                        "width": width,
                        "url": request.build_absolute_uri(default_storage.url(path)),
                    }
                )
    return items


def _iso_z(dt) -> str:
    return dt.isoformat().replace("+00:00", "Z")


def _annotate_posts_with_likes(queryset, user):
    queryset = queryset.annotate(likes_count=Count("likes", distinct=True))
    if user.is_authenticated:
        queryset = queryset.annotate(
            liked_by_me=Exists(
                Like.objects.filter(post_id=OuterRef("pk"), user_id=user.id)
            )
        )
    return queryset


def _post_likes_fields(post: Post, request) -> dict:
    if hasattr(post, "likes_count"):
        likes_count = post.likes_count
    else:
        likes_count = post.likes.count()
    liked_by_me = False
    if request.user.is_authenticated:
        if hasattr(post, "liked_by_me"):
            liked_by_me = bool(post.liked_by_me)
        else:
            liked_by_me = post.likes.filter(user_id=request.user.id).exists()
    return {"likes_count": likes_count, "liked_by_me": liked_by_me}


def serialize_post(post: Post, request) -> dict:
    image_url = None
    if post.image:
        image_url = request.build_absolute_uri(post.image.url)
    return {
        "id": post.id,
        "caption": post.text,
        "status": post.status,
        "author": {"username": post.user.username},
        "width": post.width,
        "height": post.height,
        "exif": post.exif or {},
        "image": image_url,
        "derivatives": _derivative_payload(post, request),
        **_post_likes_fields(post, request),
        "created_at": _iso_z(post.created_at),
        "updated_at": _iso_z(post.updated_at),
    }


def _can_view_comment(user, comment: Comment) -> bool:
    if comment.status == Comment.Status.VISIBLE:
        return True
    if not user.is_authenticated:
        return False
    if comment.user_id == user.id:
        return True
    return _is_leader(user)


def _get_viewable_comment(user, comment_id: int) -> Comment:
    comment = get_object_or_404(Comment, pk=comment_id)
    if not _can_view_post(user, comment.post):
        raise NotFound()
    if not _can_view_comment(user, comment):
        raise NotFound()
    return comment


def _comments_visible_qs(user, post: Post):
    qs = Comment.objects.filter(post=post)
    if _is_leader(user):
        return qs
    if user.is_authenticated:
        return qs.filter(
            Q(status=Comment.Status.VISIBLE) | Q(user_id=user.id)
        )
    return qs.filter(status=Comment.Status.VISIBLE)


def _serialize_reply(comment: Comment) -> dict:
    return {
        "id": comment.id,
        "text": comment.text,
        "status": comment.status,
        "author": {"username": comment.user.username},
        "parent_id": comment.parent_id,
        "created_at": _iso_z(comment.created_at),
        "updated_at": _iso_z(comment.updated_at),
    }


def serialize_comment(comment: Comment, replies: list[Comment]) -> dict:
    return {
        "id": comment.id,
        "text": comment.text,
        "status": comment.status,
        "author": {"username": comment.user.username},
        "parent_id": comment.parent_id,
        "created_at": _iso_z(comment.created_at),
        "updated_at": _iso_z(comment.updated_at),
        "replies": [_serialize_reply(reply) for reply in replies],
    }


def _resolve_comment_parent(post: Post, parent_id) -> Comment | None:
    if parent_id is None:
        return None
    parent = get_object_or_404(Comment, pk=parent_id, post=post)
    if parent.parent_id is None:
        return parent
    return parent.parent


def _validate_comment_text(text) -> str:
    if text is None:
        text = ""
    text = str(text)
    if len(text) > 1000:
        raise ValidationError(
            {"text": ["Ensure this field has no more than 1000 characters."]}
        )
    if not text.strip():
        raise ValidationError({"text": ["This field may not be blank."]})
    return text


def _create_post(user, caption: str, image) -> Post:
    from posts.images import ContentHashConflict, build_derivatives

    if len(caption) > 2000:
        raise ValidationError(
            {"caption": ["Ensure this field has no more than 2000 characters."]}
        )
    if not image:
        raise ValidationError({"image": ["This field is required."]})

    built = build_derivatives(image)
    if Post.objects.filter(user=user, content_hash=built["content_hash"]).exists():
        raise ContentHashConflict()

    post = Post(
        user=user,
        text=caption,
        width=built["width"],
        height=built["height"],
        exif=built["exif"],
        content_hash=built["content_hash"],
    )
    post.save()
    if hasattr(image, "seek"):
        image.seek(0)
    post.image.save(image.name, image, save=True)
    _save_derivatives(post, built["files"])
    if not post.slug:
        post.slug = str(post.id)
        post.save(update_fields=["slug"])
    return post


class PostListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        status_param = request.query_params.get("status")
        if status_param == "hidden":
            if not _is_leader(request.user):
                raise PermissionDenied()
            queryset = Post.objects.filter(status=Post.Status.HIDDEN)
        else:
            queryset = Post.objects.filter(status=Post.Status.VISIBLE)

        queryset = _annotate_posts_with_likes(queryset, request.user)
        page = CursorPagination().paginate(queryset, request)
        page["results"] = [serialize_post(post, request) for post in page["results"]]
        return Response(page)

    def post(self, request):
        caption = request.data.get("caption", "")
        if caption is None:
            caption = ""
        caption = str(caption)
        from posts.images import ContentHashConflict

        try:
            post = _create_post(request.user, caption, request.data.get("image"))
        except ContentHashConflict:
            raise Conflict()
        return Response(serialize_post(post, request), status=201)


class PostDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, pk):
        post = _get_viewable_post(request.user, pk)
        post = _annotate_posts_with_likes(Post.objects.filter(pk=post.pk), request.user).get()
        return Response(serialize_post(post, request))

    def patch(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.user_id != request.user.id:
            raise PermissionDenied()
        if "caption" in request.data:
            caption = request.data.get("caption")
            if caption is None:
                caption = ""
            caption = str(caption)
            if len(caption) > 2000:
                raise ValidationError(
                    {"caption": ["Ensure this field has no more than 2000 characters."]}
                )
            post.text = caption
            post.slug = slugify(caption[:50]) if caption else str(post.id)
            post.save()
        return Response(serialize_post(post, request))

    def delete(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.user_id != request.user.id:
            raise PermissionDenied()
        post.delete()
        return Response(status=204)


class PostHideView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not _is_leader(request.user):
            raise PermissionDenied()
        post = get_object_or_404(Post, pk=pk)
        post.status = Post.Status.HIDDEN
        post.save(update_fields=["status", "updated_at"])
        return Response(serialize_post(post, request))


class PostRestoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not _is_leader(request.user):
            raise PermissionDenied()
        post = get_object_or_404(Post, pk=pk)
        post.status = Post.Status.VISIBLE
        post.save(update_fields=["status", "updated_at"])
        return Response(serialize_post(post, request))


class PostCommentListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, pk):
        post = _get_viewable_post(request.user, pk)
        visible = _comments_visible_qs(request.user, post)
        roots = visible.filter(parent__isnull=True)
        page = CursorPagination().paginate(roots, request)
        root_ids = [comment.id for comment in page["results"]]
        replies_by_root: dict[int, list[Comment]] = {rid: [] for rid in root_ids}
        if root_ids:
            for reply in visible.filter(parent_id__in=root_ids).order_by("created_at", "id"):
                replies_by_root[reply.parent_id].append(reply)
        page["results"] = [
            serialize_comment(comment, replies_by_root.get(comment.id, []))
            for comment in page["results"]
        ]
        return Response(page)

    def post(self, request, pk):
        post = _get_viewable_post(request.user, pk)
        text = _validate_comment_text(request.data.get("text"))
        parent_id = request.data.get("parent_id")
        if parent_id is not None:
            try:
                parent_id = int(parent_id)
            except (TypeError, ValueError):
                raise ValidationError({"parent_id": ["A valid integer is required."]})
        parent = _resolve_comment_parent(post, parent_id)
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            text=text,
            parent=parent,
        )
        return Response(_serialize_reply(comment), status=201)


class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        comment = _get_viewable_comment(request.user, pk)
        if comment.user_id != request.user.id:
            raise PermissionDenied()
        if "text" in request.data:
            comment.text = _validate_comment_text(request.data.get("text"))
            comment.save(update_fields=["text", "updated_at"])
        return Response(_serialize_reply(comment))

    def delete(self, request, pk):
        comment = _get_viewable_comment(request.user, pk)
        if comment.user_id != request.user.id:
            raise PermissionDenied()
        comment.delete()
        return Response(status=204)


class CommentHideView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not _is_leader(request.user):
            raise PermissionDenied()
        comment = get_object_or_404(Comment, pk=pk)
        comment.status = Comment.Status.HIDDEN
        comment.save(update_fields=["status", "updated_at"])
        return Response(_serialize_reply(comment))


class CommentRestoreView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not _is_leader(request.user):
            raise PermissionDenied()
        comment = get_object_or_404(Comment, pk=pk)
        comment.status = Comment.Status.VISIBLE
        comment.save(update_fields=["status", "updated_at"])
        return Response(_serialize_reply(comment))


class PostLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def _serialized_post(self, request, post_id: int) -> Response:
        post = _get_viewable_post(request.user, post_id)
        post = _annotate_posts_with_likes(Post.objects.filter(pk=post.pk), request.user).get()
        return Response(serialize_post(post, request))

    def put(self, request, pk):
        post = _get_viewable_post(request.user, pk)
        Like.objects.get_or_create(user=request.user, post=post)
        return self._serialized_post(request, pk)

    def delete(self, request, pk):
        post = _get_viewable_post(request.user, pk)
        Like.objects.filter(user=request.user, post=post).delete()
        return self._serialized_post(request, pk)
