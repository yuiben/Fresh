from rest_framework.exceptions import APIException
from rest_framework import status

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
        "message":{
            "password": "The password specified is invalid. Please check password"
        }
    }


class InvalidPhoneNumberException(BaseException):
    default_detail = {
        "status":400,
        "message":{
            "phone_number":"The phone number is invalid. Please check phone number."
        }
    }

class InvalidDateOfBirthException(BaseException):
    default_detail = {
        "status":400,
        "data":{
            "date_of_birth":"The date of birth is in valid. Please check date of birth"
        }
    }
