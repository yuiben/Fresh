from django.urls import reverse
from faker import Faker
from rest_framework.test import APITestCase

from device_mngr_auth.common.exceptions import UserNotFoundException
from device_mngr_auth.auth_user.models import DMAUser, Position, UserProfile
from rest_framework.test import RequestsClient

class TestSetUp(APITestCase):
    param = Faker()
    def creat_user_with_test_case(self,password):
        position = Position.objects.create(name= self.param.name())
        user = DMAUser.objects.create(email=self.param.email(),name='admin',password=password,role=1)
        UserProfile.objects.create(
            user=user,position=position, first_name='admin', last_name='admin', phone_number='0367101750',date_of_birth='2020-08-09')
        
        return user
        
    def setUp(self):
        self.login_url = reverse('login')
        self.auth_user_url = reverse('user')
        self.auth_admin_url = reverse('admin')
        self.list_create_user = reverse('user-list')
        password = self.param.email()
        self.user_data = {
            'email': self.creat_user_with_test_case(password).email,
            'password': password,
        }
        self.create_user_data = {
            "name" : self.param.name(),
            "email": self.param.email(),
            "role": 1,
            "profile": {
                "first_name": self.param.name(),
                "last_name": self.param.name(),
                "phone_number": '0' + f'{self.param.random_number(digits=9)}',
                "date_of_birth": self.param.date(),
                "position": self.creat_user_with_test_case(password).profile.position.id,
            }
        }

        

    def tearDown(self):
        return super().tearDown()