from django.db import models

from device_mngr_auth.common.models import BaseModel
from device_mngr_auth.core.models import Category, Brand


class Device(BaseModel, models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    description = models.TextField()
    image = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='category_device')
    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name='brand_device')

    class Meta:
        db_table = 'devices'