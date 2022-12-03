from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from rest_framework import serializers

from device_mngr_auth.core.models import Order


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Order Input',
            value={
                'user': {
                    'name': 'admin',
                    'email': 'admin@gmail.com',
                    'line_id': '',
                    'profile': {
                        'first_name': 'admin',
                        'last_name': 'admin',
                        'phone_number': '000000000',
                        'date_of_birth': '1-1-1997',
                        'position': 1
                    }
                },
                'user_id': 1,
                'line_id': ''
            },
            request_only=False,
            response_only=False,
        ),
    ],
)
class OrderSerializer(serializers.ModelSerializer):
    user_id = serializers.CharField(max_length=255, allow_null=True, required=False)

    class Meta:
        model = Order
        fields = ['user_id']
