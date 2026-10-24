import { useParams } from "react-router-dom";

export default function PostPage() {
  const { id } = useParams();

  return (
    <section>
      <h1>Пост {id}</h1>
    </section>
  );
}
