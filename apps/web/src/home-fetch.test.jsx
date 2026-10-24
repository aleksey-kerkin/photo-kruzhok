import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import HomePage from "./pages/HomePage.jsx";

describe("HomePage fetch", () => {
  it("shows an error when the feed request fails", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: false,
        status: 500,
        json: async () => ({}),
      })),
    );

    render(
      <QueryClientProvider
        client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}
      >
        <HomePage />
      </QueryClientProvider>,
    );

    expect(await screen.findByText("Не удалось загрузить ленту.")).toBeTruthy();
    vi.unstubAllGlobals();
  });
});
