from django.urls import path

from accounts.views import LoginView, LogoutView, MeView, RefreshView, RegisterView

urlpatterns = [
    path("login", LoginView.as_view()),
    path("register", RegisterView.as_view()),
    path("refresh", RefreshView.as_view()),
    path("logout", LogoutView.as_view()),
    path("me", MeView.as_view()),
]
