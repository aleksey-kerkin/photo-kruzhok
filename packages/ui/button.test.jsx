import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Button } from "./src/Button.jsx";
import { Field } from "./src/Field.jsx";

describe("Field", () => {
  it("renders a labeled input", () => {
    render(<Field id="caption" label="Подпись" />);
    expect(screen.getByLabelText("Подпись")).toBeTruthy();
  });
});

describe("Button", () => {
  it("primary button exposes name Сохранить and class pk-button--primary", () => {
    render(<Button variant="primary">Сохранить</Button>);
    const control = screen.getByRole("button", { name: "Сохранить" });
    expect(control.classList.contains("pk-button--primary")).toBe(true);
  });
});
