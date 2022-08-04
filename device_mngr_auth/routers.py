from rest_framework import routers

from device_mngr_auth.auth_user.urls import auth_urls

router = routers.SimpleRouter(trailing_slash=False)
urlpatterns = (
        router.urls + auth_urls)
