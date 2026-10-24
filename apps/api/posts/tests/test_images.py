import io
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


def test_build_derivatives_includes_all_widths_for_wide_image():
    buf = io.BytesIO()
    Image.new("RGB", (2000, 1000), color=(10, 20, 30)).save(buf, format="JPEG")
    result = build_derivatives(_uploaded_file(buf.getvalue()))

    assert set(result["files"]["webp"].keys()) == {480, 960, 1600}
    assert set(result["files"]["avif"].keys()) == {480, 960, 1600}

