import { expect, test } from "@playwright/test";

test("home page shows the Russian showcase heading", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Фото-кружок" })).toBeVisible();
});
