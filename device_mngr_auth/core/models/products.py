from django.db import models

from device_mngr_auth.common.models import BaseModel
from device_mngr_auth.core.models import Category


class Product(BaseModel):
    name = models.CharField(max_length=100, default=None, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='categories')

    class Meta:
        db_table = 'Product'
