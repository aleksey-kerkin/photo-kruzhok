import { lazy } from "react";
import { Route, Routes } from "react-router-dom";

import AppShell from "./components/AppShell.jsx";

const HomePage = lazy(() => import("./pages/HomePage.jsx"));
const NewPostPage = lazy(() => import("./pages/NewPostPage.jsx"));
const PostPage = lazy(() => import("./pages/PostPage.jsx"));
const ProfilePage = lazy(() => import("./pages/ProfilePage.jsx"));
const EditProfilePage = lazy(() => import("./pages/EditProfilePage.jsx"));
const ChallengePage = lazy(() => import("./pages/ChallengePage.jsx"));
const LoginPage = lazy(() => import("./pages/LoginPage.jsx"));
const RegisterPage = lazy(() => import("./pages/RegisterPage.jsx"));

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<HomePage />} />
        <Route path="posts/new" element={<NewPostPage />} />
        <Route path="posts/:id" element={<PostPage />} />
        <Route path="profiles/:username" element={<ProfilePage />} />
        <Route path="profiles/me/edit" element={<EditProfilePage />} />
        <Route path="challenges/current" element={<ChallengePage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
      </Route>
    </Routes>
  );
}
