from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.response import Response

from device_mngr_auth.auth_user.serializers import AuthLoginSerializer


@extend_schema(request=AuthLoginSerializer, responses={200: {}}, methods=['POST'],)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def auth_login_view(request):
    auth_serializer = AuthLoginSerializer(data=request.data)
    auth_serializer.is_valid()
    token = auth_serializer.authenticate()
    return Response(token, 200)


@extend_schema(request=None, responses={200: {}}, methods=['POST'],)
@api_view(["POST"])
def auth_verify_token_view(request):
    return Response(request.user, 200)
