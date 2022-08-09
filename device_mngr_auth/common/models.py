from django.db import models


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    deleted_at = models.DateField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True