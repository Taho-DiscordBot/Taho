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
from taho.abc import Shortcutable


if TYPE_CHECKING:
    from ..models import Shortcut, BaseModel
    from taho.enums import ShortcutType


__all__ = (
    "create_shortcut",
    "get_shortcut",
)

async def create_shortcut(type_: ShortcutType, model: Shortcutable) -> Shortcut:
    """|coro|

    Creates a shortcut for the given model.

    Parameters
    -----------
    type_: :class:`~taho.enums.ShortcutType`
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

    from taho.database.models import shortcut

    shortcut_class = getattr(shortcut, type_.value)

    shortcut = await shortcut_class.get_or_create(
        **{
            "type": data[0],
            data[1]: model,
        }
    )
    return shortcut[0]


async def get_shortcut(model: BaseModel, field_name: str) -> Shortcutable:
    """|coro|

    Gets the shortcut for the given model and field name.

    Parameters
    -----------
    model: :class:`~taho.database.models.base.BaseModel`
        The model to get the shortcut for.
    field_name: :class:`str`
        The name of the field to get the shortcut for.
    
    Returns
    --------
    :class:`~taho.abc.Shortcutable`
        The shortcut.    
    """
    id_name = field_name + "_id"
    short_name = field_name.replace("_shortcut", "")
    field_value_name = "_" + short_name
    if hasattr(model, id_name) and hasattr(model, field_value_name):
        shortcut = getattr(model, field_value_name)
        if isinstance(shortcut, Shortcutable):
            return shortcut
        else:
            shortcut = await shortcut.get()
            setattr(model, field_value_name, shortcut)
            return shortcut
    elif hasattr(model, id_name) and not hasattr(model, field_value_name):
        shortcut: Shortcut = await getattr(model, field_name)
        shortcut = await shortcut.get()
        setattr(model, field_value_name, shortcut)
        return shortcut