import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import App from "./App.jsx";
import ChallengePage from "./pages/ChallengePage.jsx";
import EditProfilePage from "./pages/EditProfilePage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import NewPostPage from "./pages/NewPostPage.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
import RegisterPage from "./pages/RegisterPage.jsx";

function renderRoute(path, element) {
  return render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path={path} element={element} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("static Russian headings", () => {
  it("renders sign-in", async () => {
    renderRoute("/login", <LoginPage />);
    expect(await screen.findByRole("heading", { name: "Вход" })).toBeTruthy();
  });

  it("renders upload", async () => {
    renderRoute("/posts/new", <NewPostPage />);
    expect(await screen.findByRole("heading", { name: "Новый пост" })).toBeTruthy();
  });

  it("renders registration", async () => {
    renderRoute("/register", <RegisterPage />);
    expect(await screen.findByRole("heading", { name: "Регистрация" })).toBeTruthy();
  });

  it("renders profile", async () => {
    render(
      <QueryClientProvider client={new QueryClient()}>
        <MemoryRouter initialEntries={["/profiles/anya"]}>
          <Routes>
            <Route path="/profiles/:username" element={<ProfilePage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );
    expect(await screen.findByRole("heading", { name: "Профиль anya" })).toBeTruthy();
  });

  it("renders profile edit", async () => {
    renderRoute("/profiles/me/edit", <EditProfilePage />);
    expect(
      await screen.findByRole("heading", { name: "Редактирование профиля" }),
    ).toBeTruthy();
  });

  it("renders challenge", async () => {
    renderRoute("/challenges/current", <ChallengePage />);
    expect(await screen.findByRole("heading", { name: "Текущий челлендж" })).toBeTruthy();
  });
});

describe("App routes", () => {
  it("renders the feed heading at /", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: true,
        json: async () => ({ results: [], next_cursor: null, has_next: false }),
      })),
    );

    render(
      <QueryClientProvider client={new QueryClient()}>
        <MemoryRouter initialEntries={["/"]}>
          <App />
        </MemoryRouter>
      </QueryClientProvider>,
    );

    expect(await screen.findByRole("heading", { name: "Лента" })).toBeTruthy();
    vi.unstubAllGlobals();
  });
});
