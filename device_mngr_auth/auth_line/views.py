from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema, OpenApiParameter
from linebot.exceptions import LineBotApiError
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from device_mngr_auth.auth_line.serializers import AuthLoginSerializer
from device_mngr_auth.auth_line.services import LineServices
from device_mngr_auth.auth_user.views import line_bot_api


@extend_schema(
    responses={200: {}},
    methods=['GET'],
    parameters=[OpenApiParameter(name='ad_code', required=True, type=str)]
)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
@csrf_exempt
def auth_line(request):
    line_services = LineServices()
    response = line_services.get_auth_url(request)
    return Response({'result': response})


@extend_schema(
    responses={200: {}},
    methods=['GET'],
    parameters=[OpenApiParameter(name='ad_code', required=True, type=str)])
@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
@csrf_exempt
def add_tracking_line(request):
    return Response('friend-fail')


@extend_schema(
    responses={200: {}},
    methods=['GET'],
    parameters=[OpenApiParameter(name='ad_code', required=True, type=str)])
@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
@csrf_exempt
def get_token(request):
    line_services = LineServices()
    token = line_services.return_token_access(request)
    return Response(token)


@extend_schema(
    responses={200: {}},
    methods=['GET'],
    parameters=[OpenApiParameter(name='redirect_url', required=True, type=str)]
)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
@csrf_exempt
def line_login(request):
    line_services = LineServices()
    token = line_services.line_login(request)
    return Response({'data': token})


@extend_schema(
    request=AuthLoginSerializer,
    responses={200: {}},
    methods=['POST'],
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
@csrf_exempt
def line_verify_get_info_user(request):
    line_services = LineServices()
    data = line_services.line_verify_get_info_user(request)
    return Response({'data': data})


@extend_schema(
    responses={200: {}},
    methods=['GET'],
)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
@csrf_exempt
def callback_view(request):
    return Response({'data': request.GET})
