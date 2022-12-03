from django.db import models

from device_mngr_auth.common.models import BaseModel


class GiftProduct(BaseModel):
    gift = models.ForeignKey('Gift', on_delete=models.PROTECT, related_name='gift_product')
    product = models.ForeignKey('Product', on_delete=models.PROTECT, related_name='gift_product')
    product_sku = models.ForeignKey('AttributeValue', on_delete=models.PROTECT, related_name='gift_product')

    class Meta:
        db_table = 'gift_product'
