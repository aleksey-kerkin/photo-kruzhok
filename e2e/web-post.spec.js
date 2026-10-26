import { expect, test } from "@playwright/test";

test("post page renders", async ({ page }) => {
  await page.goto("/posts/1");
  const image = page.locator("img");
  const missing = page.getByRole("heading", { name: "Пост не найден" });
  await expect(image.or(missing)).toBeVisible();
});
