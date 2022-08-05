from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme


class MDAAuthenticationScheme(SimpleJWTScheme):
    target_class = "device_mngr_auth.common.auth.JWTAuth"
    name = "DMUAuthentication"
