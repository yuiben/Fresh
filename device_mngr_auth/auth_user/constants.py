from enum import Enum


class DMAUserRoleType(int, Enum):
    ADMIN = 1
    USER = 2
    
class DefaultPasswordUser(str, Enum):
    PASSWORD = "user2020"
