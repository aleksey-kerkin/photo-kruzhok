import { createClient } from "@photo-kruzhok/sdk";

import { useAccessToken } from "./useAccessToken.js";

export function useApiClient() {
  const { accessToken } = useAccessToken();

  return createClient({
    fetchImpl: (path, init) => fetch(path, init),
    getAccessToken: () => accessToken.value,
    refresh: async () => {},
  });
}
