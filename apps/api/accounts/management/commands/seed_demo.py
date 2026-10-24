import hashlib
import os
from datetime import timedelta
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.models import Profile
from challenges.models import Challenge, Submission, Vote
from feed.models import Announcement, FeaturedWork
from posts.api import _create_post
from posts.images import ContentHashConflict
from posts.models import Comment, Like, Post

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "fixtures" / "photos"

AUTHORS = ("anya", "kirill", "nina", "mark")

CAPTIONS = (
    "Утренний свет в парке",
    "Тень от каштанов",
    "После дождя на асфальте",
    "Окно кафе на рассвете",
    "Лестница во дворе",
    "Отражение в луже",
    "Крыши и антенны",
    "Пешеходный переход",
    "Скамейка у воды",
    "Графит на стене",
    "Мост через канал",
    "Силуэт на закате",
    "Зимний двор",
    "Снег на ветках",
    "Трамвайная остановка",
    "Неон у входа",
    "Коридор подъезда",
    "Листья у бордюра",
    "Чайник на столе",
    "Книги на подоконнике",
    "Дождь за стеклом",
    "Велосипед у подъезда",
    "Свет фонаря ночью",
    "Тихая улица вечером",
)

CARD_EXIF = (
    {
        "camera": "Demo Camera Mk I",
        "lens": "35mm f/2",
        "focal_length_mm": 35,
        "aperture": 2.8,
        "shutter_speed": "1/250",
        "iso": 200,
    },
    {
        "camera": "Demo Camera Mk II",
        "lens": "50mm f/1.8",
        "focal_length_mm": 50,
        "aperture": 4.0,
        "shutter_speed": "1/125",
        "iso": 400,
    },
    {
        "camera": "Demo Camera Mk III",
        "lens": "24mm f/2.8",
        "focal_length_mm": 24,
        "aperture": 5.6,
        "shutter_speed": "1/60",
        "iso": 800,
    },
    {
        "camera": "Demo Camera Mk IV",
        "lens": "85mm f/1.4",
        "focal_length_mm": 85,
        "aperture": 2.0,
        "shutter_speed": "1/500",
        "iso": 100,
    },
)

OPEN_CHALLENGE_TITLE = "Неделя контраста"
OPEN_CHALLENGE_DESCRIPTION = (
    "Снимите город или интерьер, где свет и тень читаются с первого взгляда."
)

SHOWCASE_POST_INDEXES = (0, 3, 7, 11, 15, 19)

ANNOUNCEMENTS = (
    (
        "Добро пожаловать в фотокружок",
        "Мы открыли ленту и витрину. Загружайте кадры, комментируйте и "
        "участвуйте в открытой теме недели.",
    ),
    (
        "Тема недели уже открыта",
        "Отправьте один кадр в «Неделю контраста» до конца срока. "
        "Голосование доступно всем участникам.",
    ),
)

COMMENTS = (
    (0, "kirill", "Свет здесь очень мягкий, нравится."),
    (0, "nina", "Кадр спокойный, хорошо лег в ленту."),
    (1, "anya", "Тень добавляет глубины."),
    (2, "mark", "Отражения получились живыми."),
    (5, "kirill", "Композиция ровная, без лишнего."),
    (8, "anya", "Очень атмосферно у воды."),
    (12, "nina", "Зима передана точно."),
    (18, "mark", "Домашний кадр выглядит тепло."),
)

LIKES = (
    ("kirill", 0),
    ("nina", 0),
    ("mark", 0),
    ("anya", 1),
    ("kirill", 2),
    ("nina", 3),
    ("mark", 5),
    ("anya", 8),
    ("kirill", 12),
    ("nina", 18),
    ("mark", 22),
)

SUBMISSION_POST_INDEXES = (2, 9, 14, 21)

VOTES = (
    ("anya", 0),
    ("kirill", 1),
    ("nina", 2),
)


class Command(BaseCommand):
    help = "Load idempotent demo data for the photo circle."

    def handle(self, *args, **options):
        member_password = os.environ.get("DEMO_MEMBER_PASSWORD")
        leader_password = os.environ.get("DEMO_LEADER_PASSWORD")
        if not member_password or not leader_password:
            raise CommandError(
                "DEMO_MEMBER_PASSWORD and DEMO_LEADER_PASSWORD must be set."
            )

        with transaction.atomic():
            users = self._ensure_users(member_password, leader_password)
            posts = self._ensure_posts(users)
            self._ensure_comments(users, posts)
            self._ensure_likes(users, posts)
            challenge = self._ensure_open_challenge(users["kirill"])
            submissions = self._ensure_submissions(challenge, posts)
            self._ensure_votes(users, challenge, submissions)
            self._ensure_showcase(posts)
            self._ensure_announcements(users["kirill"])

        self.stdout.write(self.style.SUCCESS("Demo seed complete."))

    def _ensure_users(self, member_password, leader_password):
        user_model = get_user_model()
        specs = (
            ("anya", member_password, False, "Аня"),
            ("kirill", leader_password, True, "Кирилл"),
            ("nina", None, False, "Нина"),
            ("mark", None, False, "Марк"),
        )
        users = {}
        for username, password, is_leader, display_name in specs:
            user, created = user_model.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@demo.photo-kruzhok.local"},
            )
            if password:
                user.set_password(password)
            else:
                user.set_unusable_password()
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.display_name = display_name
            profile.is_leader = is_leader
            profile.save()
            users[username] = user
        return users

    def _photo_paths(self):
        if not FIXTURES_DIR.is_dir():
            raise CommandError(f"Fixture directory missing: {FIXTURES_DIR}")
        paths = sorted(FIXTURES_DIR.glob("*.jpg"))
        if len(paths) != 24:
            raise CommandError(
                f"Expected 24 JPEG fixtures in {FIXTURES_DIR}, found {len(paths)}."
            )
        return paths

    def _ensure_posts(self, users):
        paths = self._photo_paths()
        posts = []
        for index, path in enumerate(paths):
            author_name = AUTHORS[index % len(AUTHORS)]
            caption = CAPTIONS[index]
            post = self._ensure_post(users[author_name], path, caption, index)
            posts.append(post)
        return posts

    def _ensure_post(self, user, path: Path, caption: str, index: int) -> Post:
        raw = path.read_bytes()
        content_hash = hashlib.sha256(raw).hexdigest()
        existing = Post.objects.filter(user=user, content_hash=content_hash).first()
        if existing:
            if existing.text != caption:
                existing.text = caption
                existing.save(update_fields=["text"])
            self._fill_exif_if_missing(existing, index)
            return existing

        with path.open("rb") as handle:
            uploaded = File(handle, name=path.name)
            try:
                post = _create_post(user, caption, uploaded)
            except ContentHashConflict:
                post = Post.objects.get(user=user, content_hash=content_hash)

        self._fill_exif_if_missing(post, index)
        return post

    def _fill_exif_if_missing(self, post: Post, index: int) -> None:
        if post.exif:
            return
        post.exif = dict(CARD_EXIF[index % len(CARD_EXIF)])
        post.save(update_fields=["exif"])

    def _ensure_comments(self, users, posts):
        for post_index, username, text in COMMENTS:
            Comment.objects.get_or_create(
                post=posts[post_index],
                user=users[username],
                text=text,
            )

    def _ensure_likes(self, users, posts):
        for username, post_index in LIKES:
            Like.objects.get_or_create(
                user=users[username],
                post=posts[post_index],
            )

    def _ensure_open_challenge(self, leader) -> Challenge:
        now = timezone.now()
        challenge, _ = Challenge.objects.get_or_create(
            title=OPEN_CHALLENGE_TITLE,
            defaults={
                "description": OPEN_CHALLENGE_DESCRIPTION,
                "start": now - timedelta(days=2),
                "end": now + timedelta(days=12),
                "status": Challenge.Status.OPEN,
                "created_by": leader,
            },
        )
        challenge.description = OPEN_CHALLENGE_DESCRIPTION
        challenge.start = now - timedelta(days=2)
        challenge.end = now + timedelta(days=12)
        challenge.status = Challenge.Status.OPEN
        challenge.created_by = leader
        challenge.save()
        return challenge

    def _ensure_submissions(self, challenge, posts):
        submissions = []
        for post_index in SUBMISSION_POST_INDEXES:
            submission, _ = Submission.objects.get_or_create(
                challenge=challenge,
                post=posts[post_index],
            )
            submissions.append(submission)
        return submissions

    def _ensure_votes(self, users, challenge, submissions):
        for username, submission_index in VOTES:
            Vote.objects.update_or_create(
                user=users[username],
                challenge=challenge,
                defaults={"submission": submissions[submission_index]},
            )

    def _ensure_showcase(self, posts):
        for order, post_index in enumerate(SHOWCASE_POST_INDEXES, start=1):
            FeaturedWork.objects.update_or_create(
                order=order,
                defaults={"post": posts[post_index]},
            )

    def _ensure_announcements(self, author):
        now = timezone.now()
        for offset_days, (title, body) in enumerate(ANNOUNCEMENTS):
            published_at = now - timedelta(days=7 - offset_days)
            announcement, created = Announcement.objects.get_or_create(
                title=title,
                defaults={
                    "body": body,
                    "published_at": published_at,
                    "author": author,
                },
            )
            if not created:
                announcement.body = body
                announcement.published_at = published_at
                announcement.author = author
                announcement.save()
