import { createClient } from "@photo-kruzhok/sdk";

function apiOrigin() {
  return import.meta.env.LANDING_API_ORIGIN ?? "http://127.0.0.1:8000";
}

export function createPublicClient() {
  const origin = apiOrigin().replace(/\/$/, "");
  return createClient({
    fetchImpl: (path, init) => fetch(`${origin}${path}`, init),
    getAccessToken: () => null,
    refresh: async () => {},
  });
}

function isErrorBody(body) {
  return body != null && typeof body === "object" && "code" in body && "message" in body;
}

export async function fetchProfile(client, username) {
  try {
    const body = await client.request(`/api/profiles/${encodeURIComponent(username)}`);
    if (isErrorBody(body)) {
      return null;
    }
    return body;
  } catch {
    return null;
  }
}

export async function fetchProfilePosts(client, username) {
  try {
    const body = await client.request(
      `/api/profiles/${encodeURIComponent(username)}/posts`,
    );
    if (isErrorBody(body)) {
      return null;
    }
    return body;
  } catch {
    return null;
  }
}
