from django.db import models

from device_mngr_auth.common.models import BaseModel


class Brand(BaseModel, models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)

    class Meta:
        db_table = 'brand'
