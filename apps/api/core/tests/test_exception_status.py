from rest_framework.exceptions import APIException

from core.exceptions import api_exception_handler


def test_api_exception_handler_uses_validation_error_for_unknown_status_codes():
    exc = APIException()
    exc.status_code = 418
    response = api_exception_handler(exc, {})
    assert response.status_code == 418
    assert response.data["code"] == "validation_error"
