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
from typing import TYPE_CHECKING
import uuid
from enum import Enum

if TYPE_CHECKING:
    from typing import Union, List, TypeVar
    from taho.bot import Bot

    T = TypeVar("T")

__all__ = (
    "str_to_number",
    "bot",
    "register_bot",
    "get_bot",
    "split_list",
    "_get_display",
    "get_enum_text",
    "RandomHash",
)
bot: Bot = None

def str_to_number(string: str) -> Union[int, float]:
    """
    Convert a string to a number (int or float).
    If possible, this function will return a :class:`int`.

    Parameters
    -----------
    string: str
        The string to convert.
    
    Raises
    -------
    ValueError
        If the string can't be converted to a number.
    
    Returns
    --------
    Union[:class:`int`, :class:`float`]
        The converted number.
    """
    try:
        return int(string)
    except ValueError:
        return float(string)

def register_bot(_bot: Bot) -> None:
    """
    Register the bot.
    This function is called by the bot when it is loaded.

    Parameters
    -----------
    _bot: :class:`~taho.Bot`
        The bot to register.
    """
    global bot
    bot = _bot

def get_bot() -> Bot:
    """
    Get the bot.
    This function is called by the bot when it is loaded.

    Returns
    --------
    :class:`~taho.Bot`
        The bot.
    """
    return bot

def split_list(to_split: List[T], split_at: int) -> List[List[T]]:
    """
    Split a list into a list of lists.
    This function splits a list into a list of lists, where each list has a maximum length of ``split_at``.

    Parameters
    -----------
    to_split: List[T]
        The list to split.
    split_at: int
        The maximum length of each list.

    Returns
    --------
    List[List[T]]
        The split list.
    """
    return [to_split[i:i+split_at] for i in range(0, len(to_split), split_at)]

def _get_display(value: T) -> str:
    if isinstance(value, Enum):
        return get_enum_text(value)
    else:
        return str(value)

def get_enum_text(enum: Enum) -> str:
    from taho.enums import (
        ItemType, get_item_type_text,
        RewardType, get_reward_type_text,
    )
    if isinstance(enum, ItemType):
        return get_item_type_text(enum)
    elif isinstance(enum, RewardType):
        return get_reward_type_text(enum)
    
    

class RandomHash:
    """
    A class that generates a random hash even if 
    its value is the same as another object of the 
    same type.

    Used to generate dicts and use it as keys.
    """
    def __init__(self, obj: T):
        self.obj = obj
        self.hash = hash(uuid.uuid4())

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __call__(self) -> T:
        return self.obj