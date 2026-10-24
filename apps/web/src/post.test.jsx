import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";

import PostPage from "./pages/PostPage.jsx";

function renderPostPage(postId, post, commentsPage) {
  const cache = new QueryClient();
  cache.setQueryData(["posts", String(postId)], post);
  cache.setQueryData(["posts", String(postId), "comments"], commentsPage);

  return render(
    <QueryClientProvider client={cache}>
      <MemoryRouter initialEntries={[`/posts/${postId}`]}>
        <Routes>
          <Route path="/posts/:id" element={<PostPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("PostPage", () => {
  it("shows loading and error states from the API", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => new Promise(() => {})),
    );

    render(
      <QueryClientProvider client={new QueryClient()}>
        <MemoryRouter initialEntries={["/posts/7"]}>
          <Routes>
            <Route path="/posts/:id" element={<PostPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );

    expect(screen.getByText("Загрузка…")).toBeTruthy();
    vi.unstubAllGlobals();

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
        <MemoryRouter initialEntries={["/posts/8"]}>
          <Routes>
            <Route path="/posts/:id" element={<PostPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );

    expect(await screen.findByText("Не удалось загрузить пост.")).toBeTruthy();
    vi.unstubAllGlobals();
  });

  it("renders EXIF fields and a comment from cached API payloads", () => {
    const post = {
      id: 1,
      caption: "Утренний свет в парке",
      image: "https://example.test/photo.jpg",
      width: 800,
      height: 600,
      exif: {
        camera: "Demo Camera Mk I",
        lens: "35mm f/2",
        focal_length_mm: 35,
        aperture: 2.8,
        shutter_speed: "1/250",
        iso: 200,
      },
    };
    const commentsPage = {
      results: [
        {
          id: 10,
          text: "Свет здесь очень мягкий, нравится.",
          author: { username: "kirill" },
          replies: [],
        },
      ],
      next_cursor: null,
      has_next: false,
    };

    renderPostPage(1, post, commentsPage);

    expect(screen.getByText("Demo Camera Mk I")).toBeTruthy();
    expect(screen.getByText("35mm f/2")).toBeTruthy();
    expect(screen.getByText("f/2.8")).toBeTruthy();
    expect(screen.getByText("1/250")).toBeTruthy();
    expect(screen.getByText("200")).toBeTruthy();
    expect(screen.getByText(/Свет здесь очень мягкий/)).toBeTruthy();
    expect(screen.getByText("kirill")).toBeTruthy();
  });

  it("shows not found for a missing post", async () => {
    const cache = new QueryClient();
    cache.setQueryData(["posts", "404"], null);

    render(
      <QueryClientProvider client={cache}>
        <MemoryRouter initialEntries={["/posts/404"]}>
          <Routes>
            <Route path="/posts/:id" element={<PostPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );

    expect(await screen.findByRole("heading", { name: "Пост не найден" })).toBeTruthy();
  });

  it("renders nested replies and a fallback caption", async () => {
    renderPostPage(
      5,
      { id: 5, caption: null, image: null, exif: {} },
      {
        results: [
          {
            id: 1,
            text: "Корень",
            author: { username: "anya" },
            replies: [{ id: 2, text: "Ответ", author: { username: "nina" } }],
          },
        ],
        next_cursor: null,
        has_next: false,
      },
    );

    expect(await screen.findByRole("heading", { name: "Пост 5" })).toBeTruthy();
    expect(screen.getByText(/Ответ/)).toBeTruthy();
  });

  it("shows the empty comments message", async () => {
    renderPostPage(
      6,
      { id: 6, caption: "Без комментариев", image: null, exif: {} },
      { results: [], next_cursor: null, has_next: false },
    );
    expect(await screen.findByText("Пока нет комментариев.")).toBeTruthy();
  });
});
