import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import AppShell from "./components/AppShell.jsx";

describe("AppShell", () => {
  it("exposes the main navigation landmark", () => {
    render(
      <MemoryRouter>
        <AppShell />
      </MemoryRouter>,
    );

    expect(screen.getByRole("navigation", { name: "Основная навигация" })).toBeTruthy();
  });

  it("uses the shared shell and nav classes", () => {
    const { container } = render(
      <MemoryRouter>
        <AppShell />
      </MemoryRouter>,
    );

    expect(container.querySelector(".pk-shell")).not.toBeNull();
    expect(container.querySelector(".pk-shell__nav")).not.toBeNull();
  });
});
