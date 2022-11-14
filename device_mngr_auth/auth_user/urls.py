from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from device_mngr_auth.auth_user.views import (
    soft_delete_user,
    restore_user,
    upload_data,
    LoginAPIView,
    AuthUserAPIView,
    AuthAdminAPIView,
    ListCreateUserAPIView,
    UserDetailAPIView,
    SendPasswordResetEmailView,
    UserChangePasswordView,
    UserPasswordResetView,
    UserProfileDetail,
    callback,
)

auth_urls = [
    path("list-user/", ListCreateUserAPIView.as_view(), name="user-list"),
    path("detail-user/<int:pk>/", UserDetailAPIView.as_view(), name="user-detail"),
    path("delete/", view=soft_delete_user, name="user-soft-delete"),
    path("restore/", view=restore_user, name="restore_user"),
    path("upload_data/", view=upload_data, name="upload_data"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path('user/', AuthUserAPIView.as_view(), name="user"),
    path('admin/', AuthAdminAPIView.as_view(), name="admin"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('callback/', view=callback, name='callback'),

    path("auth/profile", UserProfileDetail.as_view(), name="auth-profile"),
    path("auth/change-password", UserChangePasswordView.as_view(), name="auth-change-password"),
    path('auth/send-forgot-password-email', SendPasswordResetEmailView.as_view(), name="send-email"),
    path('auth/reset-password/<uid>/<token>', UserPasswordResetView.as_view(), name="reset-password"),
]
