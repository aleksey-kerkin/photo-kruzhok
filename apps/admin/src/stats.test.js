import { flushPromises, mount } from "@vue/test-utils";
import { QueryClient, VueQueryPlugin } from "@tanstack/vue-query";
import { beforeEach, describe, expect, it, vi } from "vitest";

import StatsPage from "./pages/StatsPage.vue";

const request = vi.fn();

vi.mock("./composables/useApiClient.js", () => ({
  useApiClient: () => ({ request }),
}));

function mountStatsPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return mount(StatsPage, {
    global: {
      plugins: [[VueQueryPlugin, { queryClient }]],
    },
  });
}

describe("stats page", () => {
  beforeEach(() => {
    request.mockReset();
  });

  it("renders counts from the stats API", async () => {
    request.mockImplementation(async (path) => {
      if (path === "/api/challenges/current") {
        return { id: 2, title: "Тема", status: "open" };
      }
      if (path === "/api/challenges/2/stats") {
        return { submissions_count: 3, votes_count: 5, participants_count: 4 };
      }
      return null;
    });

    const wrapper = mountStatsPage();
    await flushPromises();

    expect(wrapper.get("h1").text()).toBe("Статистика");
    expect(wrapper.text()).toContain("3");
    expect(wrapper.text()).toContain("5");
  });
});
