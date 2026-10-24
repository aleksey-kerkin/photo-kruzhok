import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { Button } from "./Button.jsx";
import { Field } from "./Field.jsx";

describe("Field", () => {
  it("renders a labeled input", () => {
    render(<Field id="caption" label="Подпись" />);
    expect(screen.getByLabelText("Подпись")).toBeTruthy();
  });
});

describe("Button default variant", () => {
  it("renders without the primary modifier", () => {
    render(<Button>Сохранить</Button>);
    const control = screen.getByRole("button", { name: "Сохранить" });
    expect(control.classList.contains("pk-button--primary")).toBe(false);
  });
});
