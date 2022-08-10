from rest_framework.exceptions import APIException


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



