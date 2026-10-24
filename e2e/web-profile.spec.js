import { expect, test } from "@playwright/test";

test("profile page shows the Russian heading", async ({ page }) => {
  await page.goto("/profiles/anya");
  await expect(page.getByRole("heading", { name: "Профиль anya" })).toBeVisible();
});
