from django.db import models
from django.db.models import Q

from device_mngr_auth.common.models import BaseModel
from device_mngr_auth.core.models import DMAUser
from device_mngr_auth.core.models.device_item import DeviceItem


class Borrow(BaseModel):
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
