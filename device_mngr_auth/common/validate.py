from curses.ascii import islower
from datetime import date, datetime
import re
import django.contrib.auth.password_validation as validators
from django.core import exceptions

from device_mngr_auth.common.exceptions import InvalidDateOfBirthException, InvalidPasswordException, InvalidPhoneNumberException


def validate_password(password):
    special_character = "~!@#$%^&*()_+=-.,/?\|{}[];:'\""
    lower,upper,special,digit,character_null =0,0,0,0,0
    try:
        validators.validate_password(password=password)
        for i in password:
            if(i.isupper()):
                upper += 1
                continue
            if(i.islower()):
                lower += 1
                continue
            if(i.isdigit()):
                digit += 1
                continue
            if(i.isspace()):
                character_null+=1
                continue
            if(i in special_character):
                special += 1
                continue
        if lower==0 or upper == 0 or special == 0 or digit == 0 or character_null !=0:
            raise InvalidPasswordException()
        if len(password)>30:
            raise InvalidPasswordException()
    except:
        raise InvalidPasswordException()


def validate_phone_number(phone_number):
    rule = re.compile(r'^[0]\d{9}$')
    try:
        if not rule.search(phone_number):
            raise InvalidPhoneNumberException()
    except:
        raise InvalidPhoneNumberException()

def validate_date_of_birth(date_of_birth):
    try:
        bool(datetime.strptime(date_of_birth,"%d-%m-%Y"))
        date_of = datetime.strptime(date_of_birth,"%d-%m-%Y").date()
        new_today_date = datetime.now()
        if date_of >= new_today_date.date():
            raise InvalidDateOfBirthException()
    except:
        raise InvalidDateOfBirthException()
