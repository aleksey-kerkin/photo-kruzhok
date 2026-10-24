import os
import subprocess
import sys
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model

from accounts.models import Profile

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ["USE_SQLITE"] = "1"

_repo_root = Path(__file__).resolve().parents[2]
_vips_lib_dir = _repo_root / ".vips-extract" / "usr" / "lib64"
if _vips_lib_dir.is_dir() and os.environ.get("_PK_VIPS_REEXEC") != "1":
    _lib_path = str(_vips_lib_dir)
    _existing = os.environ.get("LD_LIBRARY_PATH", "")
    _parts = [part for part in _existing.split(os.pathsep) if part]
    if _lib_path not in _parts:
        _parts.insert(0, _lib_path)
        os.environ["LD_LIBRARY_PATH"] = os.pathsep.join(_parts)
        os.environ["_PK_VIPS_REEXEC"] = "1"
        raise SystemExit(
            subprocess.call([sys.argv[0], *sys.argv[1:]], env=os.environ)
        )


@pytest.fixture
def member(db):
    user = get_user_model().objects.create_user(
        username="anya01",
        email="anya@example.com",
        password="correct-horse-battery",
    )
    Profile.objects.create(user=user)
    return user
