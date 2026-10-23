from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from posts.models import Post


@login_required
def feed(request):
    posts = Post.objects.all().order_by("-created_at")
    return render(request, "feed/feed.html", {"posts": posts})
