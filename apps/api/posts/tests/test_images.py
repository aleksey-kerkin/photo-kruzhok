from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from posts.images import build_derivatives

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
FIXTURE_PATH = FIXTURE_DIR / "sample.jpg"


@pytest.fixture
def sample_jpeg_bytes():
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    if not FIXTURE_PATH.exists():
        image = Image.new("RGB", (64, 48), color=(120, 80, 40))
        image.save(FIXTURE_PATH, format="JPEG")
    return FIXTURE_PATH.read_bytes()


def _uploaded_file(data: bytes) -> SimpleUploadedFile:
    return SimpleUploadedFile("sample.jpg", data, content_type="image/jpeg")


def test_build_derivatives_strips_gps_and_hashes_stably(sample_jpeg_bytes):
    first = build_derivatives(_uploaded_file(sample_jpeg_bytes))
    second = build_derivatives(_uploaded_file(sample_jpeg_bytes))

    assert "gps" not in first["exif"]
    assert "gps" not in second["exif"]
    assert first["content_hash"] == second["content_hash"]
    assert len(first["content_hash"]) == 64
