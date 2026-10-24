import { expect, test } from "@playwright/test";

test("demo member and leader passwords authenticate via the API", async ({ request }) => {
  const memberPassword = process.env.DEMO_MEMBER_PASSWORD;
  const leaderPassword = process.env.DEMO_LEADER_PASSWORD;
  test.skip(!memberPassword || !leaderPassword, "demo passwords are required");

  const memberResponse = await request.post("http://127.0.0.1:8000/api/auth/login", {
    data: { username: "anya", password: memberPassword },
  });
  expect(memberResponse.ok()).toBeTruthy();

  const leaderResponse = await request.post("http://127.0.0.1:8000/api/auth/login", {
    data: { username: "kirill", password: leaderPassword },
  });
  expect(leaderResponse.ok()).toBeTruthy();
});
