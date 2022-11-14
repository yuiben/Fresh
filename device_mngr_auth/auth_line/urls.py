from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from device_mngr_auth.auth_line.views import (
    auth_line,
    add_tracking_line,
    get_token,
    line_login,
    callback_view,
    line_verify_get_info_user,
)

auth_line_urls = [
    path('auth-line-url/', view=auth_line, name='callback-line'),
    path('get_token/', view=get_token, name='get_token'),
    path('add-tracking-line/', view=add_tracking_line, name='add_tracking_line'),
    path('line_login/', view=line_login, name='line_login'),
    path('line/callback_view', view=callback_view, name='line_login'),
    path('line_verify_get_info_user', view=line_verify_get_info_user, name='line_verify_get_info_user'),
]
