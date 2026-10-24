import { expect, test } from "@playwright/test";

test("feed page shows the Russian heading", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Лента" })).toBeVisible();
});
