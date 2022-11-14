from django.db import models

from device_mngr_auth.common.models import BaseModel


class Position(BaseModel):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "positions"

    def __str__(self):
        return self.name