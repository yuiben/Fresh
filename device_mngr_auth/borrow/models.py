from django.db import models
from enum import Enum
from django.db.models import Q

from device_mngr_auth.common.models import BaseModel
from device_mngr_auth.auth_user.models import DMAUser
# Create your models here.


class Category(BaseModel, models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)

    class Meta:
        db_table = 'categories'


class Brand(BaseModel, models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)

    class Meta:
        db_table = 'brands'


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


class Borrow(BaseModel, models.Model):
    borrow_date = models.DateField()
    return_date = models.DateField(default=None)
    device_item = models.ForeignKey(
        DeviceItem, on_delete=models.CASCADE, related_name='borrow')
    user = models.ForeignKey(
        DMAUser, on_delete=models.CASCADE, related_name='borrow_user')
    creator = models.ForeignKey(
        DMAUser, on_delete=models.CASCADE, related_name='borrow_creator')

    class Meta:
        db_table = 'borrows'
        constraints = [models.UniqueConstraint(fields=['device_item'], condition=Q(
            return_date__isnull=True), name='unique_device_item')]


class ReportType(BaseModel, models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'report_types'


class Report(BaseModel, models.Model):
    description = models.TextField()
    is_checked = models.BooleanField(default=False)
    report_type = models.ForeignKey(
        ReportType, on_delete=models.CASCADE, related_name='report')
    borrow = models.ForeignKey(
        Borrow, on_delete=models.CASCADE)

    class Meta:
        db_table = 'reports'
