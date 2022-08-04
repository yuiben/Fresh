from datetime import datetime

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from device_mngr_auth.auth_user.constants import DMAUserRoleType


class DMAUserManager(BaseUserManager):
    def create(self, username, password, role=DMAUserRoleType.USER, **extra_fields):
        now = datetime.now()
        user = self.model(username=username, role=role.value, **extra_fields)
        user.set_password(password)
        user.user_code = f"{int(now.timestamp())}"
        user.save()
        return user


class DMAUser(AbstractBaseUser):
    user_id = None
    first_name = None
    last_name = None
    date_joined = None
    last_login = None
    is_staff = None
    is_superuser = None
    user_group = None
    user_permission = None
    groups = None
    user_permissions = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=500, unique=True)
    password = models.CharField(max_length=255)
    role = models.IntegerField(default=DMAUserRoleType.USER.value)
    user_code = models.CharField(max_length=10)

    objects = DMAUserManager()

    class Meta:
        db_table = "auth_user"
