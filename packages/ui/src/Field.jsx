export function Field({
  id,
  label,
  error,
  invalid = false,
  className,
  inputClassName,
  ...inputProps
}) {
  const fieldClass = ["pk-field", invalid || error ? "pk-field--invalid" : null, className]
    .filter(Boolean)
    .join(" ");
  const errorId = error ? `${id}-error` : undefined;

  return (
    <div className={fieldClass}>
      <label className="pk-field__label" htmlFor={id}>
        {label}
      </label>
      <input
        id={id}
        className={["pk-field__control", inputClassName].filter(Boolean).join(" ")}
        aria-invalid={invalid || Boolean(error) || undefined}
        aria-describedby={errorId}
        {...inputProps}
      />
      {error ? (
        <p className="pk-field__error" id={errorId} role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
