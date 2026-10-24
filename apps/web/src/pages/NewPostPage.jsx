import { Field } from "@photo-kruzhok/ui/Field";

export default function NewPostPage() {
  return (
    <section>
      <h1>Новый пост</h1>
      <form>
        <label htmlFor="upload-photo">Фото</label>
        <input id="upload-photo" name="photo" type="file" accept="image/*" />
        <Field id="upload-caption" label="Подпись" name="caption" />
      </form>
    </section>
  );
}
