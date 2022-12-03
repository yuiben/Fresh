from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from device_mngr_auth.order.serializers import OrderSerializer
from device_mngr_auth.order.services import OrderServices


@extend_schema(
    tags=['order'],
    request=OrderSerializer,
    responses={200: {}},
    methods=['POST'],
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
@csrf_exempt
def create_new_order(request):
    order_service = OrderServices()
    response = order_service.create_new_order(request.data)
    return Response({'result': response})

