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
from taho.babel import _
from taho.exceptions import ValidationException
from typing import TYPE_CHECKING, overload
from taho.emoji import Emoji

if TYPE_CHECKING:
    from typing import TypeVar, Union
    T = TypeVar('T')

__all__ = (
    "required",
    "min_length",
    "max_length",
    "is_number",
    "is_int",
    "is_emoji",
    "min_value",
    "max_value",
    "forbidden_value",
)

async def required(value: T) -> bool:
    """|coro|

    Check if the value is not ``None``.

    Parameters
    -----------
    value:
        The value to check.

    Raises
    -------
    ~taho.exceptions.ValidationException
        If the value is ``None``.
    
    Returns
    --------
    :class:`bool`
        ``True`` if the value is not ``None``.
    """
    
    if value is None:
        raise ValidationException(
            _("The value is required.")
        )
            
    return True

@overload
async def min_length(value: str, min_length: int) -> bool:
    ...

@overload
async def min_length(value: list, min_length: int) -> bool:
    ...

async def min_length(value: Union[str, list], min_length: int) -> bool:
    """|coro|
    
    Check if the value is at least ``min_length`` characters long.

    Parameters
    ----------
    value: Union[:class:`str`, :class:`list`]
        The value to check.
    min_length: :class:`int`
        The minimum length of the value.
    
    Raises
    -------
    ~taho.exceptions.ValidationException
        If the value is not at least ``min_length`` characters long.
    
    Returns
    --------
    :class:`bool`
        ``True`` if the value is at least ``min_length`` characters long.
    """

    if value is None:
        return True
    
    if len(value) < min_length:
        raise ValidationException(
            _(
                "The value must be at least %(min_length)s characters long.",
                min_length=min_length
            )
        )
            
    return True

@overload
async def max_length(value: str, max_length: int) -> bool:
    ...

@overload
async def max_length(value: list, max_length: int) -> bool:
    ...

async def max_length(value: str, max_length: int) -> bool:
    """|coro|
    
    Check if the value is at most ``max_length`` characters long.
    
    Parameters
    -----------
    value: Union[:class:`str`, :class:`list`]
        The value to check.
    max_length: :class:`int`
        The maximum length of the value.
    
    Raises
    -------
    ~taho.exceptions.ValidationException
        If the value is not at most ``max_length`` characters long.
    
    Returns
    --------
    :class:`bool`
        ``True`` if the value is at most ``max_length`` characters long.
    """

    if value is None:
        return True
    
    if len(value) > max_length:
        raise ValidationException(
            _(
                "The value must be at most %(max_length)s characters long.",
                max_length=max_length
                )
        )
            
    return True

async def is_number(value: str) -> bool:
    """|coro|
    
    Check if the value can be converted to a number
    (:class:`float`).
    
    Parameters
    -----------
    value: :class:`str`
        The value to check.
    
    Raises
    -------
    ~taho.exceptions.ValidationException
        If the value can not be converted to a number.
    
    Returns
    --------
    :class:`bool`
        ``True`` if the value can be converted to a number.
    """

    if value is None:
        return True

    try:
        float(value)
    except ValueError:
        raise ValidationException(
            _("The value must be a number.")
        )
    
    return True

async def is_int(value: str) -> bool:
    """|coro|

    Check if the value can be converted to an :class:`int`.
    
    Parameters
    -----------
    value: :class:`str`
        The value to check.
    
    Raises
    -------
    ~taho.exceptions.ValidationException
        If the value can not be converted to an integer.
    
    Returns
    --------
    :class:`bool`
        ``True`` if the value can be converted to an integer.
    """

    if value is None:
        return True

    try:
        int(value)
    except ValueError:
        raise ValidationException(
            _("The value must be an integer.")
        )
    
    return True

    if value is None:
        return True

    try:
        int(value)
    except ValueError:
        raise ValidationException(
            _("The value must be an integer.")
        )

async def is_emoji(value: str) -> bool:
    """|coro|
    
    Check if the value is a valid emoji.
    
    Parameters
    -----------
    value: :class:`str`
        The value to check.
    
    Raises
    -------
    ~taho.exceptions.ValidationException
        If the value is not a valid emoji.
    
    Returns
    --------
    :class:`bool`
        ``True`` if the value is a valid emoji.
    """
    if value is None:
        return True

    emoji = Emoji(None, value)

    if not bool(emoji):
        raise ValidationException(
            _("The value must be a valid emoji.")
        )

    return True

async def min_value(value: int, min_value: int) -> bool:
    """|coro|

    Check if the value is at least ``min_value``.
    
    Parameters
    -----------
    value: :class:`int`
        The value to check.
    min_value: :class:`int`
        The minimum value of the value.
    
    Raises
    -------
    ~taho.exceptions.ValidationException
        If the value is not at least ``min_value``.
    
    Returns
    --------
    :class:`bool`
        ``True`` if the value is at least ``min_value``.
    """

    if value is None:
        return True
    
    if value < min_value:
        raise ValidationException(
            _(
                "The value must be at least %(min_value)s.",
                min_value=min_value
            )
        )
            
    return True

async def max_value(value: int, max_value: int) -> bool:
    """|coro|
    
    Check if the value is at most ``max_value``.

    Parameters
    -----------
    value: :class:`int`
        The value to check.
    max_value: :class:`int`
        The maximum value of the value.
    
    Raises
    -------
    ~taho.exceptions.ValidationException
        If the value is not at most ``max_value``.
    
    Returns
    --------
    :class:`bool`
        ``True`` if the value is at most ``max_value``.
    """

    if value is None:
        return True
    
    if value > max_value:
        raise ValidationException(
            _(
                "The value must be at most %(max_value)s.",
                max_value=max_value
            )
        )
            
    return True

async def forbidden_value(value: T, *forbidden: T) -> bool:
    """|coro|

    Check if the value is not in ``forbidden``.

    Parameters
    -----------
    value:
        The value to check.
    forbidden:
        The forbidden values.
    
    Raises
    -------
    ~taho.exceptions.ValidationException
        If the value is in ``forbidden``.
    
    Returns
    --------
    :class:`bool`
        ``True`` if the value is not in ``forbidden``.
    """

    if value is None:
        return True

    for f in forbidden:
        if value == f:
            raise ValidationException(
                _(
                    "The value %(value)s is forbidden.", 
                    value=value
                )
            )
            
    return True




