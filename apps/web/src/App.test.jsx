import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import App from "./App.jsx";

function renderAt(path) {
  vi.stubGlobal(
    "fetch",
    vi.fn(async () => ({
      ok: true,
      json: async () => ({ results: [], next_cursor: null, has_next: false }),
    })),
  );

  render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter initialEntries={[path]}>
        <App />
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("App router", () => {
  it("renders the Russian sign-in heading at /login", async () => {
    renderAt("/login");

    expect(await screen.findByRole("heading", { name: "Вход" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Войти" }).classList.contains("pk-button")).toBe(
      true,
    );
    vi.unstubAllGlobals();
  });

  it("renders the main product screens", async () => {
    const routes = [
      ["/", "Лента"],
      ["/register", "Регистрация"],
      ["/posts/new", "Новый пост"],
      ["/profiles/anya", "Профиль anya"],
      ["/profiles/me/edit", "Редактирование профиля"],
      ["/challenges/current", "Текущий челлендж"],
    ];

    for (const [path, heading] of routes) {
      renderAt(path);
      expect(await screen.findByRole("heading", { name: heading })).toBeTruthy();
      vi.unstubAllGlobals();
    }
  });
});
