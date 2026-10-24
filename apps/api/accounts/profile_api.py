from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Profile
from core.pagination import CursorPagination
from posts.api import _annotate_posts_with_likes, serialize_post
from posts.models import Post

User = get_user_model()


def serialize_profile(profile: Profile, request) -> dict:
    avatar_url = None
    if profile.avatar:
        avatar_url = request.build_absolute_uri(profile.avatar.url)
    display_name = profile.display_name or profile.user.username
    return {
        "username": profile.user.username,
        "display_name": display_name,
        "bio": profile.bio,
        "avatar": avatar_url,
    }


class ProfileDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        profile = get_object_or_404(Profile, user=user)
        return Response(serialize_profile(profile, request))


class ProfileMeView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        profile = request.user.profile
        if "display_name" in request.data:
            display_name = request.data.get("display_name")
            if display_name is None:
                display_name = ""
            display_name = str(display_name)
            if len(display_name) > 50:
                raise ValidationError(
                    {"display_name": ["Ensure this field has no more than 50 characters."]}
                )
            profile.display_name = display_name
        if "bio" in request.data:
            bio = request.data.get("bio")
            if bio is None:
                bio = ""
            bio = str(bio)
            if len(bio) > 500:
                raise ValidationError(
                    {"bio": ["Ensure this field has no more than 500 characters."]}
                )
            profile.bio = bio
        if "avatar" in request.data:
            profile.avatar = request.data.get("avatar")
        profile.save()
        return Response(serialize_profile(profile, request))


class ProfilePostsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        queryset = Post.objects.filter(
            user=user,
            status=Post.Status.VISIBLE,
        )
        queryset = _annotate_posts_with_likes(queryset, request.user)
        page = CursorPagination().paginate(queryset, request)
        page["results"] = [serialize_post(post, request) for post in page["results"]]
        return Response(page)
