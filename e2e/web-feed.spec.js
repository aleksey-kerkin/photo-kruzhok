import { expect, test } from "@playwright/test";

test("feed page shows the Russian heading and a post card", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Лента" })).toBeVisible();
  await expect(page.locator(".pk-feed__card").first()).toBeVisible();
});
