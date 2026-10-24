import { flushPromises, mount } from "@vue/test-utils";
import { QueryClient, VueQueryPlugin } from "@tanstack/vue-query";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ChallengePage from "./pages/ChallengePage.vue";

const request = vi.fn();

vi.mock("./composables/useApiClient.js", () => ({
  useApiClient: () => ({ request }),
}));

function mountChallengePage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return mount(ChallengePage, {
    global: {
      plugins: [[VueQueryPlugin, { queryClient }]],
    },
  });
}

describe("challenge page", () => {
  beforeEach(() => {
    request.mockReset();
  });

  it("renders the theme heading and submission list", async () => {
    request.mockImplementation(async (path) => {
      if (path === "/api/challenges/current") {
        return { id: 1, title: "Неделя света", status: "open" };
      }
      if (path === "/api/challenges/1/submissions") {
        return {
          results: [{ id: 10, post: { caption: "Заявка участника" } }],
        };
      }
      return null;
    });

    const wrapper = mountChallengePage();
    await flushPromises();

    expect(wrapper.get("h1").text()).toBe("Тема");
    expect(wrapper.text()).toContain("Заявки");
    expect(wrapper.text()).toContain("Заявка участника");
  });

  it("casts a vote for a submission", async () => {
    request.mockImplementation(async (path, init) => {
      if (path === "/api/challenges/current") {
        return { id: 1, title: "Неделя света", status: "open" };
      }
      if (path === "/api/challenges/1/submissions") {
        return { results: [{ id: 10, post: { caption: "Голос" } }] };
      }
      if (path === "/api/challenges/1/votes" && init?.method === "POST") {
        return { submission_id: 10 };
      }
      return null;
    });

    const wrapper = mountChallengePage();
    await flushPromises();
    await wrapper.get("button").trigger("click");
    await flushPromises();

    expect(request).toHaveBeenCalledWith(
      "/api/challenges/1/votes",
      expect.objectContaining({ method: "POST" }),
    );
  });
});
