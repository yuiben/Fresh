from enum import Enum


class DBEnumFields(str, Enum):
    ORDER = "order"
    ATTRIBUTE = 'attribute'
    ATTRIBUTE_VALUE = 'attribute_value'
