from .enums import InfoType
from typing import Any

__all__ = (
    "convert_to_type",
    "get_type"
)


def convert_to_type(value: Any, type_: InfoType) -> Any:
    if type_ == InfoType.NULL:
        return None
    converters = {
        InfoType.BOOL: bool,
        InfoType.INT: int,
        InfoType.STRING: str,
        InfoType.FLOAT: float
    }
    return converters[type_](value)

def get_type(value: Any) -> InfoType:
    if value is None:
        return InfoType.NULL
    types = {
        bool: InfoType.BOOL,
        int: InfoType.INT,
        str: InfoType.STRING,
        float: InfoType.FLOAT
    }
    return types[type(value)]