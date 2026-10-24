import { flushPromises, mount } from "@vue/test-utils";
import { QueryClient, VueQueryPlugin } from "@tanstack/vue-query";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ModerationPage from "./pages/ModerationPage.vue";

const request = vi.fn();

vi.mock("./composables/useApiClient.js", () => ({
  useApiClient: () => ({ request }),
}));

function mountModerationPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return mount(ModerationPage, {
    global: {
      plugins: [[VueQueryPlugin, { queryClient }]],
    },
  });
}

describe("moderation", () => {
  beforeEach(() => {
    request.mockReset();
  });

  it("renders Недостаточно прав when the API returns permission_denied", async () => {
    request.mockResolvedValue({
      code: "permission_denied",
      message: "Forbidden",
      fields: {},
    });

    const wrapper = mountModerationPage();
    await flushPromises();

    expect(wrapper.text()).toContain("Недостаточно прав");
  });
});
