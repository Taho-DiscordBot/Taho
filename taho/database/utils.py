"""
The MIT License (MIT)

Copyright (c) 2022-present Taho-DiscordBot

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
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