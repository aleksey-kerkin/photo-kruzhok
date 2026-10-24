import { expect, test } from "@playwright/test";

test("registration page shows the Russian heading", async ({ page }) => {
  await page.goto("/register");
  await expect(page.getByRole("heading", { name: "Регистрация" })).toBeVisible();
});
