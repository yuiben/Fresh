from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from device_mngr_auth.common.models import BaseModel

from device_mngr_auth.auth_user.constants import DMAUserRoleType

class DMAUserManager(BaseUserManager):
    def create(self, email, name, password, role=DMAUserRoleType.USER, **extra_fields):
        user = self.model(email=email, name=name, role=role, **extra_fields)
        user.set_password(password)
        user.save()
        return user


class Position(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    class Meta:
        db_table = "positions"
        
    def __str__(self):
        return self.name
    

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
    
    objects = DMAUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        

class UserProfile(BaseModel):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    image = models.TextField(default=None, null=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='positions')
    user = models.OneToOneField(DMAUser, on_delete=models.CASCADE, related_name='profile')

    class Meta:
        '''
        to set table name in database
        '''
        db_table = "profile"


