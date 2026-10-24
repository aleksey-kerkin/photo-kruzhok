from django.conf import settings
from django.db import models


class FeaturedWork(models.Model):
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="featured_slots",
    )
    order = models.PositiveSmallIntegerField(unique=True)

    class Meta:
        ordering = ["order", "id"]


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
    published_at = models.DateTimeField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="announcements",
    )

    class Meta:
        ordering = ["-published_at", "-id"]
