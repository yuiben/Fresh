from device_mngr_auth.auth_line.services import LineServices
from device_mngr_auth.auth_user.serializers import UserCreateSerializer
from device_mngr_auth.core.models import DMAUser
from device_mngr_auth.order.serializers import OrderSerializer


class OrderServices:
    @classmethod
    def create_new_order(cls, request):
        user = request.get('user', None)
        user_id = request.pop('user_id', None)
        line_id = request.get('line_id', None)

        if line_id and user_id:
            line_service = LineServices()
            line_service.save_line_id_to_user(line_id, user_id)

        if not user_id:
            user_id = cls.create_user_from_order(user)

        user_data = {'user_id': user_id}
        data = cls.create_order(request=user_data)
        return data

    @classmethod
    def create_user_from_order(cls, request):
        serializer = UserCreateSerializer(data=request)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data.get('id')

    @classmethod
    def create_order(cls, request):
        order = OrderSerializer(data=request)
        order.is_valid(raise_exception=True)
        order.save()
        return order.data
