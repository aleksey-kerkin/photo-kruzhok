import { expect, test } from "@playwright/test";

test("sign-in page shows the Russian heading", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("heading", { name: "Вход" })).toBeVisible();
});
