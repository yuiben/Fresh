from django.db import models

from device_mngr_auth.common.models import BaseModel
from device_mngr_auth.core.models.borrow import Borrow
from device_mngr_auth.core.models.report_type import ReportType


class Report(BaseModel, models.Model):
    description = models.TextField()
    is_checked = models.BooleanField(default=False)
    report_type = models.ForeignKey(
        ReportType, on_delete=models.CASCADE, related_name='report')
    borrow = models.ForeignKey(
        Borrow, on_delete=models.CASCADE)

    class Meta:
        db_table = 'reports'