from django.db import models

from device_mngr_auth.auth_user.models import DMAUser
from device_mngr_auth.common.constants.db_table import DBEnumFields
from device_mngr_auth.common.models import BaseModel


class Order(BaseModel):
    user = models.ForeignKey(DMAUser, on_delete=models.PROTECT, related_name='order')

    class Meta:
        db_table = DBEnumFields.ORDER.value
