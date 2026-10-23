from django.urls import path

from posts.views import PostCreateView, PostListView

urlpatterns = [
    path("", PostListView.as_view(), name="post_list"),
    path("create/", PostCreateView.as_view(), name="post_create"),
]
