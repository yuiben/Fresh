from django.db import models

from device_mngr_auth.common.models import BaseModel


class GiftProductTarget(BaseModel):
    gift = models.ForeignKey('Gift', on_delete=models.PROTECT, related_name='gift_product_target')
    product = models.ForeignKey('Product', on_delete=models.PROTECT, related_name='gift_product_target')

    class Meta:
        db_table = 'gift_product_target'
