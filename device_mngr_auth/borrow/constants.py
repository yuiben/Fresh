from enum import Enum
from .models import Borrow, Device, Report
from device_mngr_auth.auth_user.models import DMAUser


class ModelItems(Enum):
    BORROW = Borrow
    DEVICE = Device
    REPORT = Report
    USER = DMAUser
    

class Month(int, Enum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12