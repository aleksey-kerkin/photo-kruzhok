/**
 * @param {{
 *   fetchImpl: typeof fetch;
 *   getAccessToken: () => string | null | undefined;
 *   refresh: () => Promise<void>;
 * }} options
 */
export function createClient({ fetchImpl, getAccessToken, refresh }) {
  async function request(path, init = {}) {
    return performRequest(path, init, false);
  }

  async function performRequest(path, init, retried) {
    const headers = new Headers(init.headers ?? {});
    const token = getAccessToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetchImpl(path, { ...init, headers });

    if (response.status === 401) {
      if (!retried) {
        await refresh();
        return performRequest(path, init, true);
      }
      return response.json();
    }

    if (!response.ok) {
      return response.json();
    }

    return response.json();
  }

  return { request };
}
