import { expect, test } from "@playwright/test";

test("challenge page exposes the vote screen landmark", async ({ page }) => {
  await page.goto("/challenges/current");
  await expect(page.getByRole("heading", { name: "Текущий челлендж" })).toBeVisible();
});
