import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

const EXIF_FIELDS = [
  { key: "camera", label: "Камера" },
  { key: "lens", label: "Объектив" },
  { key: "focal_length_mm", label: "Фокусное расстояние", format: (v) => `${v} мм` },
  { key: "aperture", label: "Диафрагма", format: (v) => `f/${v}` },
  { key: "shutter_speed", label: "Выдержка" },
  { key: "iso", label: "ISO", format: (v) => String(v) },
  {
    key: "taken_at",
    label: "Дата съёмки",
    format: (v) => {
      const date = new Date(v);
      return Number.isNaN(date.getTime())
        ? String(v)
        : date.toLocaleString("ru-RU");
    },
  },
];

async function fetchPost(id) {
  const response = await fetch(`/api/posts/${id}`);
  if (response.status === 404) {
    return null;
  }
  if (!response.ok) {
    throw new Error("Post request failed");
  }
  return response.json();
}

async function fetchComments(id) {
  const response = await fetch(`/api/posts/${id}/comments`);
  if (!response.ok) {
    throw new Error("Comments request failed");
  }
  return response.json();
}

function ExifList({ exif }) {
  const rows = EXIF_FIELDS.filter(({ key }) => exif?.[key] != null && exif[key] !== "");
  if (rows.length === 0) {
    return null;
  }

  return (
    <dl className="pk-post__exif">
      {rows.map(({ key, label, format }) => (
        <div key={key}>
          <dt>{label}</dt>
          <dd>{format ? format(exif[key]) : exif[key]}</dd>
        </div>
      ))}
    </dl>
  );
}

function CommentItem({ comment }) {
  return (
    <li className="pk-post__comment">
      <p>
        <strong>{comment.author.username}</strong>: {comment.text}
      </p>
      {comment.replies?.length > 0 ? (
        <ul className="pk-post__replies">
          {comment.replies.map((reply) => (
            <li key={reply.id} className="pk-post__comment">
              <p>
                <strong>{reply.author.username}</strong>: {reply.text}
              </p>
            </li>
          ))}
        </ul>
      ) : null}
    </li>
  );
}

export default function PostPage() {
  const { id } = useParams();

  const {
    data: post,
    isPending: postPending,
    error: postError,
  } = useQuery({
    queryKey: ["posts", id],
    queryFn: () => fetchPost(id),
  });

  const { data: commentsPage, isPending: commentsPending } = useQuery({
    queryKey: ["posts", id, "comments"],
    queryFn: () => fetchComments(id),
    enabled: post != null,
  });

  if (postPending) {
    return (
      <section>
        <p>Загрузка…</p>
      </section>
    );
  }

  if (postError) {
    return (
      <section>
        <p>Не удалось загрузить пост.</p>
      </section>
    );
  }

  if (post === null) {
    return (
      <section>
        <h1>Пост не найден</h1>
        <p>Такого поста нет или он недоступен.</p>
      </section>
    );
  }

  const comments = commentsPage?.results ?? [];

  return (
    <article className="pk-post">
      <h1>{post.caption ?? `Пост ${post.id}`}</h1>
      {post.image ? (
        <img
          className="pk-post__image"
          src={post.image}
          alt={post.caption ?? ""}
          width={post.width}
          height={post.height}
        />
      ) : null}
      {post.caption ? <p className="pk-post__caption">{post.caption}</p> : null}
      <ExifList exif={post.exif} />
      <section aria-labelledby="post-comments-heading">
        <h2 id="post-comments-heading">Комментарии</h2>
        {commentsPending ? <p>Загрузка комментариев…</p> : null}
        {comments.length === 0 && !commentsPending ? (
          <p>Пока нет комментариев.</p>
        ) : (
          <ul className="pk-post__comments">
            {comments.map((comment) => (
              <CommentItem key={comment.id} comment={comment} />
            ))}
          </ul>
        )}
      </section>
    </article>
  );
}
