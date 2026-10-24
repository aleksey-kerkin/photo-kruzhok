import { useParams } from "react-router-dom";

export default function ProfilePage() {
  const { username } = useParams();

  return (
    <section>
      <h1>Профиль {username}</h1>
    </section>
  );
}
