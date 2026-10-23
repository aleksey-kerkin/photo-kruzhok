from pathlib import Path

from django.conf import settings


def test_base_dir_is_the_api_package():
    assert settings.BASE_DIR.name == "api"
    assert settings.MEDIA_URL == "/media/"
    assert settings.MEDIA_ROOT == settings.BASE_DIR / "media"


def test_manage_py_lives_beside_core():
    manage = Path(settings.BASE_DIR) / "manage.py"
    assert manage.is_file()
