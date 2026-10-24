function buttonClassName(variant, className) {
  return ["pk-button", variant === "primary" ? "pk-button--primary" : null, className]
    .filter(Boolean)
    .join(" ");
}

export function Button({ variant, className, children, type = "button", ...props }) {
  return (
    <button type={type} className={buttonClassName(variant, className)} {...props}>
      <span className="pk-button__label">{children}</span>
    </button>
  );
}
