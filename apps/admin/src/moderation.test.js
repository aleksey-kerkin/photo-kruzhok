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

  it("renders hidden posts and restores them", async () => {
    request.mockImplementation(async (path, init) => {
      if (path === "/api/posts?status=hidden") {
        return { results: [{ id: 5, caption: "Скрытый пост" }] };
      }
      if (path === "/api/posts/5/restore" && init?.method === "POST") {
        return { id: 5, caption: "Скрытый пост", status: "visible" };
      }
      return null;
    });

    const wrapper = mountModerationPage();
    await flushPromises();

    expect(wrapper.text()).toContain("Скрытый пост");
    await wrapper.get("button").trigger("click");
    await flushPromises();
    expect(request).toHaveBeenCalledWith("/api/posts/5/restore", { method: "POST" });
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
