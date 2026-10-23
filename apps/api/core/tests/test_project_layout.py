import subprocess
import sys
from pathlib import Path

from django.conf import settings


def test_base_dir_is_the_api_package():
    assert settings.BASE_DIR.name == "api"
    assert settings.MEDIA_URL == "/media/"
    assert settings.MEDIA_ROOT == settings.BASE_DIR / "media"


def test_manage_py_lives_beside_core():
    manage = Path(settings.BASE_DIR) / "manage.py"
    assert manage.is_file()


def test_importing_settings_does_not_set_use_sqlite():
    api_root = Path(settings.BASE_DIR)
    script = """
import os
os.environ.pop("USE_SQLITE", None)
os.environ["SECRET_KEY"] = "subprocess-test-secret"
os.environ["DATABASE_URL"] = "postgres://u:p@localhost:5432/db"
import core.settings
assert os.environ.get("USE_SQLITE") is None
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=api_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout
