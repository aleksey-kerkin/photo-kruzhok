import { flushPromises, mount } from "@vue/test-utils";
import { createMemoryHistory, createRouter } from "vue-router";
import { describe, expect, it } from "vitest";

import App from "./App.vue";
import { routes } from "./router.js";

describe("App router", () => {
  it("renders the Russian leader sign-in heading at /login", async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes,
    });

    const wrapper = mount(App, {
      global: {
        plugins: [router],
      },
    });

    await router.push("/login");
    await flushPromises();

    expect(wrapper.get("h1").text()).toBe("Вход руководителя");
  });
});
