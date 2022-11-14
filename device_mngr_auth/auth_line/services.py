from social_django.utils import load_backend, load_strategy
import requests
import random
import string

from device_mngr_auth.auth_line.line_oauth import LineAuthentication


class LineServices:
    def get_auth_url(self, request):
        ad_code = request.GET['ad_code']
        provider = 'line'
        redirect_uri = f'http://127.0.0.1:8000/api/v1/get_token/?ad_code={ad_code}'
        redirect_uri_param = 'ad_code=aggressive'
        strategy = load_strategy(request)

        strategy.session_set(redirect_uri_param, redirect_uri)
        backend = load_backend(strategy, provider, redirect_uri=redirect_uri)
        authorization_url = backend.auth_url()
        return authorization_url

    def return_token_access(self, request):
        redirect_uri = f'https://6ecc-171-225-184-118.ap.ngrok.io/api/v1/callback/'
        token = self.issue_access_token(redirect_uri, request.GET['code'])
        return token

    def get_random_string(self, length):
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str

    def issue_access_token(self, redirect_uri, code):
        client_id = '1657557069'
        client_secret = 'd6c02e214838e6e09380c056a47f34da'
        access_token_url = 'https://api.line.me/oauth2/v2.1/token'
        get_response = requests.post(access_token_url,
                                     data={
                                         "grant_type": "authorization_code",
                                         "code": code,
                                         "redirect_uri": redirect_uri,
                                         "client_id": client_id,
                                         "client_secret": client_secret,
                                         "code_verifier": self.get_random_string(43),
                                     })  # HTTP Request
        return get_response

    @classmethod
    def line_login(cls, request):
        redirect_url = request.GET.get('redirect_url', None)
        strategy = load_strategy(request)
        backend = load_backend(strategy, 'line', redirect_uri=redirect_url)
        authorization_url = backend.auth_url()
        return authorization_url

    @classmethod
    def line_verify_get_info_user(cls, request):
        line_auth = LineAuthentication()
        strategy = load_strategy(request)
        response_token = cls.authentication_line(request, strategy)
        id_token = response_token.get('id_token', None)
        info_user = line_auth.line_auth_verify(id_token=id_token)
        return info_user

    @classmethod
    def authentication_line(cls, request, strategy):
        try:
            redirect_url = request.data.get('redirect_url', None)
            backend = load_backend(strategy, 'line', redirect_uri=redirect_url)
            response = backend.auth_complete()
            return response
        except Exception as e:
            return None


