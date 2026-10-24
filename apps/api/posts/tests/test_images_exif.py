from fractions import Fraction

from posts.images import (
    _aperture,
    _camera_name,
    _focal_length_mm,
    _iso,
    _shutter_speed,
    _taken_at,
)


def test_camera_name_joins_make_and_model():
    assert _camera_name({"Make": "Canon", "Model": "EOS R5"}) == "Canon EOS R5"


def test_focal_length_mm_reads_rational_values():
    assert _focal_length_mm({"FocalLength": Fraction(50, 1)}) == 50.0


def test_aperture_reads_float_values():
    assert _aperture({"FNumber": 2.8}) == 2.8


def test_shutter_speed_formats_fractional_exposure():
    assert _shutter_speed({"ExposureTime": Fraction(1, 250)}) == "1/250"


def test_iso_reads_photographic_sensitivity():
    assert _iso({"PhotographicSensitivity": 400}) == 400


def test_taken_at_returns_utc_iso_string():
    assert _taken_at({"DateTimeOriginal": "2024:06:01 12:30:00"}) == "2024-06-01T12:30:00Z"


def test_camera_name_returns_model_when_make_is_missing():
    assert _camera_name({"Model": "EOS R5"}) == "EOS R5"


def test_focal_length_mm_returns_none_for_invalid_values():
    assert _focal_length_mm({"FocalLength": "not-a-number"}) is None


def test_shutter_speed_returns_string_for_long_exposure():
    assert _shutter_speed({"ExposureTime": Fraction(2, 1)}) == "2s"


def test_taken_at_returns_none_for_invalid_date():
    assert _taken_at({"DateTimeOriginal": "not-a-date"}) is None
