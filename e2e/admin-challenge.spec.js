import { expect, test } from "@playwright/test";

test("weekly theme page shows the Russian heading", async ({ page }) => {
  await page.goto("/challenge");
  await expect(page.getByRole("heading", { name: "Тема" })).toBeVisible();
});
