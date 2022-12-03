from django.db import models

from device_mngr_auth.common.constants.db_table import DBEnumFields
from device_mngr_auth.common.models import BaseModel
from device_mngr_auth.core.models import Product
from device_mngr_auth.core.models.attribute import Attribute


class AttributeValue(BaseModel):
    value = models.CharField(max_length=255, default=None, null=True)
    attribute = models.ForeignKey(Attribute, on_delete=models.PROTECT, related_name='attribute')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='attribute')

    class Meta:
        db_table = DBEnumFields.ATTRIBUTE_VALUE.value
