import calendar

from django.db.models.functions import TruncMonth
from django.db.models import Count, F

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions


from device_mngr_auth.auth_user.permissions import IsAdminUser
from device_mngr_auth.borrow.constants import ModelItems, Month
from device_mngr_auth.core.models import Report
from device_mngr_auth.core.models.device_item import DeviceItemStatuses, DeviceItem


# Create your views here.
class DashboardAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated, IsAdminUser,)

    def total_device_item(self):
        result = []
        total_item = DeviceItem.objects.filter(
            status_id__in=(
                DeviceItemStatuses.AVAILABLE.value, 
                DeviceItemStatuses.IN_USE.value)
            ).values('status_id').annotate(total=Count('status_id'))
        for value in total_item:
            result.append({
                'type': DeviceItemStatuses(int(value['status_id'])).name.lower(),
                'value': value['total']})
        return result

    def chart_report(self):
        data = []
        month = Report.objects.values(
            month=('created_at__month'),
            type_report=('report_type__name')
        ).annotate(total=Count('report_type_id')).order_by('created_at__month')
        
        for i in range(1, 13):
            data.append({
                'month': Month(i).name.capitalize(),
                'broken': 0,
                'missing': 0
            })
        for model in month:
            # print(model)
            result = {
                'month': Month(model['month']).name.capitalize(),
                model['type_report'].lower(): model['total']
            }
            data[model['month']-1].update(result)
        return data

    def report_summary(self):
        result = []
        missing, broken = [0]*13, [0]*13

        report_missing = Report.objects.filter(report_type=1, deleted_at__isnull=True).annotate(
            month=TruncMonth('created_at')).values('month').annotate(total=Count('id'))

        report_broken = Report.objects.filter(report_type=2, deleted_at__isnull=True).annotate(
            month=TruncMonth('created_at')).values('month').annotate(total=Count('id'))

        for value in report_missing:
            month = value['month'].month
            missing[month] = value['total']

        for value in report_broken:
            month = value['month'].month
            broken[month] = value['total']

        report_types = ['Missing', 'Broken']
        for report_type in report_types:
            count = missing if report_type == 'Missing' else broken
            for i in range(1, 13):
                result.append({
                    'month': calendar.month_name[i],
                    'value': count[i],
                    'type': report_type
                })
        return result

    def get(self, request):
        result = {}
        
        for model in ModelItems:
            data = model.value.objects.filter(deleted_at=None)
            data = {f'{model.name.lower()}': len(data)}
            result.update(data)
            
        result.update({'device_item': self.total_device_item()})
        result.update({'chart': self.report_summary()})
        return Response({'code': 200, 'message': 'success', 'data': result})
