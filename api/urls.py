from django.urls import path
from .views import HelloView, AuthRegisterView, AuthLoginView, AuthMeView

urlpatterns = [
    path("hello/", HelloView.as_view(), name="hello"),
    path("auth/register/", AuthRegisterView.as_view(), name="auth-register"),
    path("auth/login/", AuthLoginView.as_view(), name="auth-login"),
    path("auth/me/", AuthMeView.as_view(), name="auth-me"),
]
