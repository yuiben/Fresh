from rest_framework import routers

from device_mngr_auth.auth_user.urls import auth_urls
from device_mngr_auth.dashboard.urls import dashboard_urls
from device_mngr_auth.auth_line.urls import auth_line_urls
from device_mngr_auth.order.urls import order_urls


router = routers.SimpleRouter(trailing_slash=False)
urlpatterns = (
        router.urls + auth_urls + dashboard_urls + auth_line_urls + order_urls)

