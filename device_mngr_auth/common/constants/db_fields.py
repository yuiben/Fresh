from enum import Enum


class DBOrderFields(str, Enum):
    ID = 'id'
    USER_ID = 'user_id'
    TOTAL = 'total'
