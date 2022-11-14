import json

import requests
from social_core.backends.line import LineOAuth2


class LineAuthentication(LineOAuth2):
    name = 'line'
    AUTHORIZATION_URL = 'https://access.line.me/oauth2/v2.1/authorize'
    ACCESS_TOKEN_URL = 'https://api.line.me/oauth2/v2.1/token'
    BASE_API_URL = 'https://api.line.me'
    VERIFY_URL = 'https://api.line.me/oauth2/v2.1/verify'
    USER_INFO_URL = BASE_API_URL + '/v2/profile'
    ACCESS_TOKEN_METHOD = 'POST'
    VERIFY_TOKEN_METHOD = 'POST'
    STATE_PARAMETER = True
    DEFAULT_SCOPE = ['profile', 'openid', 'chat_message.write']

    def auth_params(self, state=None):
        client_id, client_secret = self.get_key_and_secret()
        return {
            'response_type': self.RESPONSE_TYPE,
            'client_id': client_id,
            'redirect_uri': self.get_redirect_uri(),
            'state': self.get_or_create_state(),
            'scope': self.get_scope()
        }

    def auth_complete(self, *args, **kwargs):
        print(self.auth_complete_params())
        try:
            response = self.request_access_token(
                self.access_token_url(),
                method=self.ACCESS_TOKEN_METHOD,
                headers=self.auth_headers(),
                data=self.auth_complete_params()
            )
            return response
        except requests.HTTPError as err:
            self.process_error(json.loads(err.response.content))

    def line_auth_verify(self, id_token):
        try:
            response = self.get_json(
                self.VERIFY_URL,
                method=self.VERIFY_TOKEN_METHOD,
                headers=self.auth_headers(),
                data=self.auth_param_verify(id_token)
            )
            return response
        except requests.HTTPError as err:
            self.process_error(err.response.json())

    def auth_param_verify(self, id_token):
        client_id, _ = self.get_key_and_secret()
        return {
            'id_token': id_token,
            'client_id': client_id,
        }
