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
});
