from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Post(models.Model):
    class Status(models.TextChoices):
        VISIBLE = "visible", "Visible"
        HIDDEN = "hidden", "Hidden"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to="posts/images/", blank=True, null=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    exif = models.JSONField(default=dict)
    content_hash = models.CharField(max_length=64, blank=True, default="")
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.VISIBLE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(
        max_length=255, unique_for_date="created_at", editable=False
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}'s post at {self.created_at.strftime('%Y-%m-%d %H:%M')}"  # noqa: E501

    def save(self, *args, **kwargs):
        if not self.slug and self.text:
            self.slug = slugify(self.text[:50])
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            "posts:post_detail",
            args=[
                self.created_at.year,
                self.created_at.month,
                self.created_at.day,
                self.slug,
            ],
        )


class Comment(models.Model):
    class Status(models.TextChoices):
        VISIBLE = "visible", "Visible"
        HIDDEN = "hidden", "Hidden"

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.CharField(max_length=1000)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.VISIBLE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "id"]


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_like_per_user_post"),
        ]
