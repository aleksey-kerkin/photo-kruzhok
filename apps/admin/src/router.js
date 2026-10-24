import { createRouter, createWebHistory } from "vue-router";

import ChallengePage from "./pages/ChallengePage.vue";
import LoginPage from "./pages/LoginPage.vue";
import ModerationPage from "./pages/ModerationPage.vue";
import StatsPage from "./pages/StatsPage.vue";

export const routes = [
  { path: "/login", component: LoginPage },
  { path: "/challenge", component: ChallengePage },
  { path: "/moderation", component: ModerationPage },
  { path: "/stats", component: StatsPage },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
