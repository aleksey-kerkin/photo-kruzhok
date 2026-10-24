from django.urls import path

from accounts.views import LoginView, RegisterView

urlpatterns = [
    path("login", LoginView.as_view()),
    path("register", RegisterView.as_view()),
]
