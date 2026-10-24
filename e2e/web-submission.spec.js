import { expect, test } from "@playwright/test";

test("current challenge page shows the Russian heading", async ({ page }) => {
  await page.goto("/challenges/current");
  await expect(page.getByRole("heading", { name: "Текущий челлендж" })).toBeVisible();
});
