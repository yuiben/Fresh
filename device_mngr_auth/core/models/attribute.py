from django.db import models

from device_mngr_auth.common.constants.db_table import DBEnumFields
from device_mngr_auth.common.models import BaseModel


class Attribute(BaseModel):
    name = models.CharField(max_length=100, default=None, null=True)

    class Meta:
        db_table = DBEnumFields.ATTRIBUTE.value
