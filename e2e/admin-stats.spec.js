import { expect, test } from "@playwright/test";

test("statistics page shows the Russian heading", async ({ page }) => {
  await page.goto("/stats");
  await expect(page.getByRole("heading", { name: "Статистика" })).toBeVisible();
});
