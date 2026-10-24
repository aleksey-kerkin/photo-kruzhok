export const PERMISSION_DENIED_MESSAGE = "Недостаточно прав";

export function isApiError(body) {
  return body != null && typeof body === "object" && "code" in body && "message" in body;
}

export function isPermissionDenied(body) {
  return isApiError(body) && body.code === "permission_denied";
}
