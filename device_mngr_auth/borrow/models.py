from contextlib import nullcontext
from email.policy import default
from lib2to3.pytree import Base
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


class Product(BaseModel):
    name = models.CharField(max_length=100, default=None, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='categories')

    class Meta:
        db_table = 'Product'


class Attribute(BaseModel):
    name = models.CharField(max_length=100, default=None, null=True)

    class Meta:
        db_table = 'Attribute'


class AttributeValue(BaseModel):
    value = models.CharField(max_length=100, default=None, null=True)
    attribue = models.ForeignKey(Attribute, on_delete=models.PROTECT, related_name='attribues')
    product = models.ForeignKey('Product', on_delete=models.PROTECT, related_name='products')

    class Meta:
        db_table = 'AttributeValue'


from django.db import models

from device_mngr_auth.common.models import BaseModel


class Gift(BaseModel):
    name = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'gift'


class GiftProduct(BaseModel):
    gift = models.ForeignKey('Gift', on_delete=models.PROTECT, related_name='gift')
    product = models.ForeignKey('Product', on_delete=models.PROTECT, related_name='products_a')
    product_sku = models.ForeignKey('AttributeValue', on_delete=models.PROTECT, related_name='product_sku')

    class Meta:
        db_table = 'gift_product'


class GiftProductTarget(BaseModel):
    gift = models.ForeignKey('Gift', on_delete=models.PROTECT, related_name='gift_target')
    product = models.ForeignKey('Product', on_delete=models.PROTECT, related_name='product_target')

    class Meta:
        db_table = 'gift_product_target'

