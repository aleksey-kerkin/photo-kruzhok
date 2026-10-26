import { expect, test } from "@playwright/test";

test("home shows the photo grid", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Фото-кружок" })).toBeVisible();
  await expect(page.locator(".pk-grid")).toBeVisible();
});
