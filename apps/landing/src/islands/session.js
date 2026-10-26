let accessToken = null;

export function getAccessToken() {
  return accessToken;
}

export function resetAccessToken() {
  accessToken = null;
}

export async function restoreAccessToken() {
  if (accessToken) {
    return accessToken;
  }
  const response = await fetch("/api/auth/refresh", {
    method: "POST",
    credentials: "include",
  });
  if (!response.ok) {
    return null;
  }
  const body = await response.json();
  accessToken = body.access ?? null;
  return accessToken;
}

export async function login({ username, password }) {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const body = await response.json();
  if (response.ok) {
    accessToken = body.access;
  }
  return { ok: response.ok, body };
}

export async function register({ username, email, password }) {
  const response = await fetch("/api/auth/register", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password }),
  });
  const body = await response.json();
  if (response.ok) {
    accessToken = body.access ?? null;
  }
  return { ok: response.ok, body };
}
