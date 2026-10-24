import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it } from "vitest";

import PostPage from "./pages/PostPage.jsx";

function renderPostPage(post, commentsPage) {
  const cache = new QueryClient();
  cache.setQueryData(["posts", "1"], post);
  cache.setQueryData(["posts", "1", "comments"], commentsPage);

  return render(
    <QueryClientProvider client={cache}>
      <MemoryRouter initialEntries={["/posts/1"]}>
        <Routes>
          <Route path="/posts/:id" element={<PostPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("PostPage", () => {
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

    renderPostPage(post, commentsPage);

    expect(screen.getByText("Demo Camera Mk I")).toBeTruthy();
    expect(screen.getByText("35mm f/2")).toBeTruthy();
    expect(screen.getByText("f/2.8")).toBeTruthy();
    expect(screen.getByText("1/250")).toBeTruthy();
    expect(screen.getByText("200")).toBeTruthy();
    expect(screen.getByText(/Свет здесь очень мягкий/)).toBeTruthy();
    expect(screen.getByText("kirill")).toBeTruthy();
  });
});
