from django.db import models

from device_mngr_auth.common.models import BaseModel


class ReportType(BaseModel, models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'report_types'