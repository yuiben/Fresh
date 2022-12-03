from enum import Enum

from django.db import models

from device_mngr_auth.common.models import BaseModel
from device_mngr_auth.core.models.device import Device


class DeviceItemStatuses(int, Enum):
    AVAILABLE = 1
    IN_USE = 2
    MISSING = 3
    BROKEN = 4


class DeviceItem(BaseModel, models.Model):
    serial_number = models.CharField(max_length=100, unique=True)
    status_id = models.IntegerField(
        default=DeviceItemStatuses.AVAILABLE.value)
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name='device_item')

    class Meta:
        db_table = 'device_items'