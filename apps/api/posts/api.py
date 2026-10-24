from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from rest_framework.exceptions import APIException, NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.pagination import CursorPagination
from posts.models import Post

DERIVATIVE_WIDTHS = (480, 960, 1600)


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
        "likes_count": 0,
        "liked_by_me": False,
        "created_at": post.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": post.updated_at.isoformat().replace("+00:00", "Z"),
    }


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
