import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import App from "./App.jsx";

describe("Upload page", () => {
  it("renders the caption field with class pk-field", async () => {
    render(
      <MemoryRouter initialEntries={["/posts/new"]}>
        <App />
      </MemoryRouter>,
    );

    expect(
      await screen.findByRole("heading", { name: "Новый пост" }),
    ).toBeTruthy();

    const caption = screen.getByLabelText("Подпись");
    expect(caption.closest(".pk-field")).not.toBeNull();
  });
});
