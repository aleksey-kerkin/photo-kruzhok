import { Link } from "react-router-dom";

export default function HomePage() {
  return (
    <section>
      <h1>Лента</h1>
      <p>
        <Link to="/posts/example">Открыть пост</Link>
      </p>
      <p>
        <Link to="/profiles/demo">Открыть профиль</Link>
      </p>
    </section>
  );
}
