import { Link, Outlet } from "react-router-dom";

export default function AppShell() {
  return (
    <div className="pk-shell">
      <header>
        <nav className="pk-shell__nav" aria-label="Основная навигация">
          <Link to="/">Лента</Link>
          <Link to="/login">Новый пост</Link>
          <Link to="/login">Редактировать профиль</Link>
          <Link to="/login">Челлендж</Link>
          <Link to="/login">Войти</Link>
          <Link to="/register">Регистрация</Link>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
