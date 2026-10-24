from rest_framework.exceptions import ValidationError

from core.exceptions import api_exception_handler


def test_api_exception_handler_formats_list_errors():
    response = api_exception_handler(ValidationError(["first", "second"]), {})
    assert response.status_code == 400
    assert response.data["message"] == "first second"
    assert response.data["fields"] == {}


def test_api_exception_handler_returns_none_for_unhandled_exceptions():
    assert api_exception_handler(Exception("boom"), {}) is None


def test_api_exception_handler_formats_field_errors():
    response = api_exception_handler(ValidationError({"caption": ["too long"]}), {})
    assert response.status_code == 400
    assert response.data["message"] == "Invalid input."
    assert response.data["fields"]["caption"] == ["too long"]
