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
from taho.enums import ShortcutableType

if TYPE_CHECKING:
    from ..models import Shortcut
    from taho.abc import Shortcutable
    from taho.enums import ShortcutType


__all__ = (
    "create_shortcut",
)

async def create_shortcut(type: ShortcutType, model: Shortcutable) -> Shortcut:
    """|coro|

    Creates a shortcut for the given model.

    Parameters
    -----------
    type: :class:`~taho.enums.ShortcutType`
        The type of the shortcut.
    model: :class:`~taho.abc.Shortcutable`
        The model to create a shortcut for.
    
    Returns
    --------
    :class:`.Shortcut`
        The created shortcut.    
    """
    from ..models import (
        Item,
        Stat,
        Currency,
        User,
        Role,
        CurrencyAmount,
    )
    converters = {
        Item: [ShortcutableType.item, "item"],
        Stat: [ShortcutableType.stat, "stat"],
        Currency: [ShortcutableType.currency, "currency"],
        User: [ShortcutableType.user, "user"],
        Role: [ShortcutableType.role, "role"],
        CurrencyAmount: [ShortcutableType.currency_amount, "currency_amount"],
    }
    data = converters[type(model)]
    shortcut = await type.value.get_or_create(
        **{
            "type": data[0],
            data[1]: model,
        }
    )
    return shortcut[0]
