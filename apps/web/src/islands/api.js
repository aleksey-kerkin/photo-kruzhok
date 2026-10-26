import { createClient } from "@photo-kruzhok/sdk";

import { getAccessToken, restoreAccessToken } from "./session.js";

export function isApiError(body) {
  return (
    body != null && typeof body === "object" && "code" in body && "message" in body
  );
}

export const api = createClient({
  fetchImpl: fetch,
  getAccessToken,
  refresh: restoreAccessToken,
});

// Multipart POST /api/posts stays on raw fetch in UploadForm.vue: the SDK
// always merges JSON-oriented headers and does not document FormData uploads.
