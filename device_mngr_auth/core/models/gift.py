from django.db import models

from device_mngr_auth.common.models import BaseModel


class Gift(BaseModel):
    name = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'gift'
