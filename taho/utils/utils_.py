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

if TYPE_CHECKING:
    from typing import Union
    from taho.bot import Bot

__all__ = (
    "str_to_number",
    "bot",
    "register_bot",
    "get_bot",
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
