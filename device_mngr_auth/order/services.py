from datetime import datetime

from django.db.models import Sum, Case, When, IntegerField, Count

from device_mngr_auth.auth_line.services import LineServices
from device_mngr_auth.auth_user.serializers import UserCreateSerializer
from device_mngr_auth.common.constants.db_fields import DBOrderFields
from device_mngr_auth.core.models import Order
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

    @classmethod
    def convert_date_time_from_to(cls, date):
        datetime_from = date + " " + "00:00:00"
        datetime_to = date + " " + "23:59:59"
        datetime_object_from = datetime.strptime(datetime_from, '%Y-%m-%d %H:%M:%S')
        datetime_object_to = datetime.strptime(datetime_to, '%Y-%m-%d %H:%M:%S')
        return str(datetime_object_from), str(datetime_object_to)

    @classmethod
    def case_when_with_optional(cls, field, keyword, then, default, output_field):
        lookup = "%s" % field
        return Case(
                    When(**{lookup: keyword}, then=then),
                    default=default,
                    output_field=output_field
                )

    @classmethod
    def order_analysis(cls, request):
        from_date_time, to_date_time = cls.convert_date_time_from_to(request.GET['date'])
        order_data_analysis = Order.objects.filter(created_at__gte=from_date_time,
                                                   created_at__lte=to_date_time)
        result = order_data_analysis.aggregate(
            total=Sum(cls.case_when_with_optional('user_id', 2, 1, 0, IntegerField())))
        return result
