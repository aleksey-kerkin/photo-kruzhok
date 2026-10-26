import { expect, test } from "@playwright/test";

test("post page renders", async ({ page }) => {
  await page.goto("/posts/1");
  await expect(page.locator("h1")).toBeVisible();
});
