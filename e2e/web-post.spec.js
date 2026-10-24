import { expect, test } from "@playwright/test";

let postId;

test.beforeAll(async ({ request }) => {
  const response = await request.get("http://127.0.0.1:8000/api/posts");
  if (!response.ok()) {
    return;
  }
  const body = await response.json();
  postId = body.results?.[0]?.id;
});

test("post page shows a caption heading", async ({ page }) => {
  test.skip(!postId, "seeded posts are required");
  await page.goto(`/posts/${postId}`);
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
});
