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
from __future__ import annotations
from taho.enums import InfoType, ShortcutableType
from typing import TYPE_CHECKING
from taho.abc import Shortcutable

if TYPE_CHECKING:
    from typing import Union
    from ..models import Shortcut, Server, Cluster
    import discord

__all__ = (
    "convert_to_type",
    "get_type",
)


def convert_to_type(value: str, type: InfoType) -> Union[None, bool, int, float, str]:
    """
    Convert a value from the DB to a certain type.

    Parameters
    -----------
    value: :class:`str`
        The value to convert.
    type: :class:`~taho.enums.InfoType`
        The type to convert to.
    
    Raises
    -------
    ValueError
        If the value is not of the correct type.
    
    Returns
    --------
    Union[None, bool, int, float, str]
        The converted value.
    """
    if type == InfoType.NULL:
        return None
    converters = {
        InfoType.BOOL: bool,
        InfoType.INT: int,
        InfoType.STR: str,
        InfoType.FLOAT: float
    }
    return converters[type](value)

def get_type(value: Union[None, bool, int, float, str]) -> InfoType:
    """
    Get the :class:`~taho.enums.InfoType` of a value.

    Parameters
    -----------
    value: Union[None, bool, int, float, str]
        The value to get the type of.
    
    Raises
    -------
    ValueError
        If the value does not correspond to an
        :class:`~taho.enums.InfoType`.
    
    Returns
    --------
    :class:`~taho.enums.InfoType`
        The :class:`~taho.enums.InfoType` that correspond
        to the value.
    """
    if value is None:
        return InfoType.NULL
    types = {
        bool: InfoType.BOOL,
        int: InfoType.INT,
        str: InfoType.STR,
        float: InfoType.FLOAT
    }
    return types[type(value)]

    #server = await create_server(guild)
    #return server.cluster