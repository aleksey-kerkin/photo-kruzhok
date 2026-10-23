from rest_framework.views import exception_handler

CODES = {
    400: "validation_error",
    401: "not_authenticated",
    403: "permission_denied",
    404: "not_found",
    409: "conflict",
    429: "too_many_requests",
}


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None
    code = CODES.get(response.status_code, "validation_error")
    message = "Request failed."
    fields = {}
    data = response.data
    if isinstance(data, dict):
        if "detail" in data:
            message = str(data["detail"])
        field_items = {
            key: value if isinstance(value, list) else [str(value)]
            for key, value in data.items()
            if key != "detail"
        }
        if field_items:
            fields = field_items
            if "detail" not in data:
                message = "Invalid input."
    elif isinstance(data, list):
        message = " ".join(str(item) for item in data)
    response.data = {"code": code, "message": message, "fields": fields}
    return response
