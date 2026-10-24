import { useEffect, useRef } from "react";

import { trapFocus } from "./focusTrap.js";

export function Dialog({ open, title, children, onClose, className, ...props }) {
  const dialogRef = useRef(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) {
      return undefined;
    }

    if (open) {
      if (!dialog.open) {
        dialog.showModal();
      }
      const panel = dialog.querySelector(".pk-dialog__panel");
      return trapFocus(panel ?? dialog);
    }

    if (dialog.open) {
      dialog.close();
    }

    return undefined;
  }, [open]);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog || !onClose) {
      return undefined;
    }

    function handleClose() {
      onClose();
    }

    dialog.addEventListener("close", handleClose);
    return () => dialog.removeEventListener("close", handleClose);
  }, [onClose]);

  return (
    <dialog ref={dialogRef} className={["pk-dialog", className].filter(Boolean).join(" ")} {...props}>
      <div className="pk-dialog__panel">
        {title ? <h2 className="pk-dialog__title">{title}</h2> : null}
        <div className="pk-dialog__body">{children}</div>
      </div>
    </dialog>
  );
}
