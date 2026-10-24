import { expect, test } from "@playwright/test";

test("upload page shows the Russian heading", async ({ page }) => {
  await page.goto("/posts/new");
  await expect(page.getByRole("heading", { name: "Новый пост" })).toBeVisible();
});
