import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Dialog } from "./src/Dialog.jsx";

describe("Dialog", () => {
  beforeEach(() => {
    HTMLDialogElement.prototype.showModal = vi.fn(function showModal() {
      this.open = true;
    });
    HTMLDialogElement.prototype.close = vi.fn(function close() {
      this.open = false;
    });
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("opens the modal and renders title and body when open", () => {
    render(
      <Dialog open title="Заголовок">
        <p>Содержимое</p>
      </Dialog>,
    );

    expect(HTMLDialogElement.prototype.showModal).toHaveBeenCalled();
    expect(screen.getByRole("heading", { name: "Заголовок" })).toBeTruthy();
    expect(screen.getByText("Содержимое")).toBeTruthy();
  });

  it("calls onClose when the dialog receives a close event", () => {
    const onClose = vi.fn();
    render(
      <Dialog open onClose={onClose}>
        <p>Тело</p>
      </Dialog>,
    );

    fireEvent(screen.getByRole("dialog"), new Event("close"));
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it("closes the modal when open becomes false", () => {
    const { rerender } = render(
      <Dialog open>
        <p>Тело</p>
      </Dialog>,
    );

    rerender(
      <Dialog open={false}>
        <p>Тело</p>
      </Dialog>,
    );

    expect(HTMLDialogElement.prototype.close).toHaveBeenCalled();
  });
});
