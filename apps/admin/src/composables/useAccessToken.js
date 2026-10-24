import { ref } from "vue";

const accessToken = ref(null);

export function useAccessToken() {
  function setAccessToken(token) {
    accessToken.value = token;
  }

  function clearAccessToken() {
    accessToken.value = null;
  }

  return {
    accessToken,
    setAccessToken,
    clearAccessToken,
  };
}
