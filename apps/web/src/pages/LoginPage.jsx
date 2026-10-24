import { Button } from "@photo-kruzhok/ui/Button";

export default function LoginPage() {
  return (
    <section>
      <h1>Вход</h1>
      <form>
        <label htmlFor="login-username">Имя пользователя или email</label>
        <input id="login-username" name="username" autoComplete="username" />
        <label htmlFor="login-password">Пароль</label>
        <input
          id="login-password"
          name="password"
          type="password"
          autoComplete="current-password"
        />
        <Button type="submit" variant="primary">Войти</Button>
      </form>
    </section>
  );
}
