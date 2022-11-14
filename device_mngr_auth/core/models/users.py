import os

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from device_mngr_auth.auth_user.constants import DMAUserRoleType
from device_mngr_auth.common.models import BaseModel


class DMAUserManager(BaseUserManager):
    def create(self, email, name, password=os.getenv("USER_DEFAULT_PASSWORD"), role=DMAUserRoleType.USER,
               **extra_fields):
        user = self.model(email=email, name=name, role=role, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class DMAUser(BaseModel, AbstractBaseUser):
    user_id = None
    first_name = None
    last_name = None
    date_joined = None
    last_login = None
    is_staff = None
    is_superuser = None
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    role = models.IntegerField(default=DMAUserRoleType.USER.value)
    code = models.CharField(max_length=255, default=None, null=True)
    line_id = models.CharField(max_length=255, default=None, null=True)

    objects = DMAUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"

    def role_value_with_id(self):
        role_value = DMAUserRoleType(self.role).name.capitalize()
        return role_value


def upload_to(instance, filename):
    return 'avatar/{filename}'.format(filename=filename)


class UserProfile(BaseModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    image = models.ImageField(upload_to=upload_to, default=None, null=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='positions')
    user = models.OneToOneField(DMAUser, on_delete=models.CASCADE, related_name='profile')

    class Meta:
        db_table = "profile"

    @property
    def full_name(self):
        full_name = self.first_name + " " + self.last_name
        return full_name






