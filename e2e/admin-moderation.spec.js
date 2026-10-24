import { expect, test } from "@playwright/test";

test("moderation page shows the Russian heading", async ({ page }) => {
  await page.goto("/moderation");
  await expect(page.getByRole("heading", { name: "Модерация" })).toBeVisible();
});
