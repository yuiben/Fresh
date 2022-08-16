
from http import client
from device_mngr_auth.auth_user.tests.test_setup import TestSetUp
from device_mngr_auth.auth_user.models import DMAUser, UserProfile, Position
from rest_framework.test import APIClient


class TestView(TestSetUp):

    def login_with_data(self):
        res = self.client.post(self.login_url, self.user_data, format='json')
        return res
        
    def check_token_headers(self):
        res = self.login_with_data()
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + res.data['access_token'])
        return client
        
    def test_user_cannot_login_with_no_data(self):
        res = self.client.post(self.login_url)
        self.assertEqual(res.status_code, 400)
        
    def test_user_login_with_data(self):
        res = self.client.post(
            self.login_url, self.user_data, format='json')
        # import pdb
        # pdb.set_trace()
        # print(f"{res.data['access_token']}")
        # print(self.user_data['password'])
        # self.assertEqual(res.data['data']['email'], self.user_data['email'])
        # self.assertEqual(res.data['data']['password'], self.user_data['password'])
        self.assertEqual(res.status_code,200)
    
    def test_auth_user_success(self):
        client = self.check_token_headers()
        res = client.post(self.auth_user_url, {})
        #print(res_check_auth_user.data)
        self.assertEqual(res.status_code,200)

    def test_auth_admin_success(self):
        client = self.check_token_headers()
        res = client.post(self.auth_admin_url,{})
        #print(res_check_auth_admin.data['data']['role'])
        self.assertEqual(res.data['data']['role'],1)
        
        
    def test_list_user(self):
        pass
    
    def test_create_user(self):
        client = self.check_token_headers()
        res = client.post(self.list_create_user, self.create_user_data, format='json')
        print(res.data['code'])
        self.assertEqual(res.data['code'], 201)
        
    
        
        