import hashlib
import io
from datetime import datetime, timezone

import pyvips
from PIL import ExifTags, Image

DERIVATIVE_WIDTHS = (480, 960, 1600)


class ContentHashConflict(Exception):
    """Raised when the same author uploads the same file hash again."""


def build_derivatives(uploaded_file):
    raw = _read_upload(uploaded_file)
    content_hash = hashlib.sha256(raw).hexdigest()

    image = Image.open(io.BytesIO(raw))
    width, height = image.size
    exif = _extract_exif(image)
    files = _encode_derivatives(image)

    return {
        "width": width,
        "height": height,
        "exif": exif,
        "content_hash": content_hash,
        "files": files,
    }


def _read_upload(uploaded_file):
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)
    data = uploaded_file.read()
    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)
    return data


def _extract_exif(image):
    exif_data = image.getexif()
    if not exif_data:
        return {}

    tag_map = {
        ExifTags.Base(tag_id).name: value
        for tag_id, value in exif_data.items()
        if tag_id in ExifTags.Base
    }
    result = {
        "camera": _camera_name(tag_map),
        "lens": _as_str(tag_map.get("LensModel")),
        "focal_length_mm": _focal_length_mm(tag_map),
        "aperture": _aperture(tag_map),
        "shutter_speed": _shutter_speed(tag_map),
        "iso": _iso(tag_map),
        "taken_at": _taken_at(tag_map),
    }
    return {key: value for key, value in result.items() if value is not None}


def _camera_name(tag_map):
    model = _as_str(tag_map.get("Model"))
    make = _as_str(tag_map.get("Make"))
    if model and make and not model.startswith(make):
        return f"{make} {model}"
    return model or make


def _as_str(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _focal_length_mm(tag_map):
    value = tag_map.get("FocalLength")
    if value is None:
        return None
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        if value.denominator == 0:
            return None
        return round(value.numerator / value.denominator, 1)
    try:
        return round(float(value), 1)
    except (TypeError, ValueError):
        return None


def _aperture(tag_map):
    value = tag_map.get("FNumber")
    if value is None:
        return None
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        if value.denominator == 0:
            return None
        return round(value.numerator / value.denominator, 1)
    try:
        return round(float(value), 1)
    except (TypeError, ValueError):
        return None


def _shutter_speed(tag_map):
    value = tag_map.get("ExposureTime")
    if value is None:
        return None
    if hasattr(value, "numerator") and hasattr(value, "denominator"):
        if value.numerator == 0 or value.denominator == 0:
            return None
        if value.numerator == 1:
            return f"1/{value.denominator}"
        seconds = value.numerator / value.denominator
        if seconds >= 1:
            return f"{seconds:g}s"
        return f"1/{round(value.denominator / value.numerator)}"
    return _as_str(value)


def _iso(tag_map):
    for key in ("PhotographicSensitivity", "ISOSpeedRatings"):
        value = tag_map.get(key)
        if value is not None:
            try:
                return int(value)
            except (TypeError, ValueError):
                continue
    return None


def _taken_at(tag_map):
    raw = tag_map.get("DateTimeOriginal") or tag_map.get("DateTime")
    if not raw:
        return None
    try:
        naive = datetime.strptime(str(raw), "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None
    return naive.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def _encode_derivatives(image):
    rgb = image.convert("RGB")
    vips_image = pyvips.Image.new_from_memory(
        rgb.tobytes(),
        rgb.width,
        rgb.height,
        3,
        "uchar",
    )

    files = {"webp": {}, "avif": {}}
    for target_width in DERIVATIVE_WIDTHS:
        if rgb.width <= target_width:
            continue
        scale = target_width / rgb.width
        resized = vips_image.resize(scale)
        actual_width = resized.width
        files["webp"][actual_width] = resized.webpsave_buffer(Q=80)
        files["avif"][actual_width] = resized.heifsave_buffer(
            compression="av1",
            Q=50,
        )
    return files
