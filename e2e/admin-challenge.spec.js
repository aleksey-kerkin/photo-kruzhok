import { expect, test } from "@playwright/test";

test("theme panel shows its heading", async ({ page }) => {
  await page.goto("/panel/challenge");
  await expect(page.getByRole("heading", { name: "Тема" })).toBeVisible();
});
