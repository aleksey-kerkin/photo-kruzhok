import { expect, test } from "@playwright/test";

test("public profile shows the member display name", async ({ page }) => {
  await page.goto("/profiles/anya");
  await expect(page.getByRole("heading", { name: "Аня" })).toBeVisible();
});
