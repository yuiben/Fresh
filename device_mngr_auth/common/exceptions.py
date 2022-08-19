from rest_framework.exceptions import APIException
from device_mngr_auth import settings
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int

from django.contrib.auth.tokens import PasswordResetTokenGenerator

class BaseException(APIException):
    status_code = 400


class EmailException(BaseException):
    default_detail = {
        "code": 400,
        "message": "Email already exists"
    }
    
class UserNotFoundException(BaseException):
    default_detail = {
        "code": 404,
        "message": "User not exists"
    }

class DuplicateEmailException(BaseException):
    default_detail = {
        "message": 400,
        "data": {
            "email": "Email is duplicated!"
        }
    }

class InvalidPasswordException(BaseException):
    default_detail = {
        "status":400,
        "message":"The password specified is invalid. Please check password"
        
    }


class InvalidPhoneNumberException(BaseException):
    default_detail = {
        "status":400,
        "message":"The phone number is invalid. Please check phone number."
        
    }

class InvalidDateOfBirthException(BaseException):
    default_detail = {
        "status":400,
        "message":"The date of birth is in valid. Please check date of birth"
        
    }

class InvalidEmailException(BaseException):
    default_detail = {
        "status":404,
        "message":"The member information for the email address you entered could not be found."
        
    }

class TokenNotFoundException(BaseException):
    default_detail = {
        "status":400,
        "message":"Token not valid"

    }

class TokenExpiredException(BaseException):
    default_detail = {
        "status":419,
        "message":"Token is expired"

    }


class CheckTokenException(PasswordResetTokenGenerator):
   def check_token(self, user, token):
        """
        Check that a password reset token is correct for a given user.
        """
        if not (user and token):
             raise TokenNotFoundException()
        # Parse the token
        try:
            ts_b36, _ = token.split("-")
        except ValueError:
             raise TokenNotFoundException()

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
             raise TokenNotFoundException()

        # Check that the timestamp/uid has not been tampered with
        for secret in [self.secret, *self.secret_fallbacks]:
            if constant_time_compare(
                self._make_token_with_timestamp(user, ts, secret),
                token,
            ):
                break
        else:
            raise TokenNotFoundException()

        # Check the timestamp is within limit.
        if (self._num_seconds(self._now()) - ts) > settings.PASSWORD_RESET_TIMEOUT:
            raise TokenExpiredException()
