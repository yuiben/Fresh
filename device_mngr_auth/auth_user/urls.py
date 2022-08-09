from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from device_mngr_auth.auth_user.views import (
    auth_login_view, 
    auth_verify_token_view,
    soft_delete_user,
    LoginAPIView , 
    AuthUserAPIView, 
    AuthAdminAPIView,
    ListCreateUserAPIView,
    ListDetailUserAPIView,
    SendPasswordResetEmailView,
    UserChangePasswordView,
    UserPasswordResetView,
    UserProfileDetail
    )

auth_urls = [
    # path("auth/login", view=auth_login_view, name="auth-login"),
    # path("auth/verify", view=auth_verify_token_view, name="auth-verify"),
    
    
    #List user
    path("list-user/", ListCreateUserAPIView.as_view(),name="list-user"),
    #List user detail
    path("list-user/<int:pk>/", ListDetailUserAPIView.as_view(),name="list-user-detail"),
    #Soft delete
    path("list-user/soft-delete/", view=soft_delete_user, name="soft delete"),
    
    
    
    #Login
    path("login/", LoginAPIView.as_view(),name="login"),
    
    #check Authen
    path('user/', AuthUserAPIView.as_view(), name="user"),
    path('admin/', AuthAdminAPIView.as_view(), name="admin"),
    
    #refresh token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    #User Profile
    path("auth/profile",UserProfileDetail.as_view(), name="auth-profile"),
    path("auth/change-password", UserChangePasswordView.as_view(), name="auth-change-password"),
    path('auth/send-forgot-password-email',SendPasswordResetEmailView.as_view(),name='send-email'),
    path('auth/reset-password/<uid>/<token>',UserPasswordResetView.as_view(),name='reset-password'),

]
