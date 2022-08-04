from django.urls import path

from device_mngr_auth.auth_user.views import auth_login_view

auth_urls = [
    path("auth/login", view=auth_login_view, name="auth-login"),
]
