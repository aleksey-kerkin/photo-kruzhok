import { expect, test } from "@playwright/test";

test("sign-in shows the submit label", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("button", { name: "Войти" })).toBeVisible();
});
