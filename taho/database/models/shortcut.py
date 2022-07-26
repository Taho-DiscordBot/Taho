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

from .base import BaseModel
from tortoise import fields
from taho.enums import ShortcutableType

if TYPE_CHECKING:
    from taho.abc import (
        Shortcutable, 
        StuffShortcutable, 
        OwnerShortcutable,
        AccessShortcutable,
        TradeStuffShortcutable
    )

__all__ = (
    "Shortcut",
    "OwnerShortcut",
    "StuffShortcut",
    "AccessShortcut",
    "TradeStuffShortcut",
)

class Shortcut(BaseModel):

    class Meta:
        abstract = True
    
    id = fields.IntField(pk=True)
    type = fields.IntEnumField(ShortcutableType)
    
    converters = {}

    def __await__(self):
        return self.get().__await__()

    async def get(self) -> Shortcutable:
        """|coro|

        Returns the shortcut's model.

        Returns
        --------
        :class:`~taho.abc.Shortcutable`
            The shortcut's model.
        """
        attr = self.converters[self.type]
        return await getattr(self, attr)

class OwnerShortcut(Shortcut):
    """Represents a shortcut to a
    :class:`~taho.abc.OwnerShortcutable` model. 
    
    See :ref:`Shortcuts <shortcut>` for more information.
    """
    class Meta:
        table = "shortcuts_owner"

    user = fields.ForeignKeyField("main.User")

    converters = {
        ShortcutableType.user: "user",
    }

    async def get(self) -> OwnerShortcutable:
        """|coro|

        Returns the shortcut's model.

        Returns
        --------
        :class:`~taho.abc.OwnerShortcutable`
            The shortcut's model.
        """
        return await super().get()

class StuffShortcut(Shortcut):
    """Represents a shortcut to a
    :class:`~taho.abc.StuffShortcutable` model. 
    
    See :ref:`Shortcuts <shortcut>` for more information.
    """
    class Meta:
        table = "shortcuts_stuff"

    item = fields.ForeignKeyField("main.Item")
    stat = fields.ForeignKeyField("main.Stat")
    role = fields.ForeignKeyField("main.Role")
    currency = fields.ForeignKeyField("main.Currency")
    inventory = fields.ForeignKeyField("main.Inventory")
    currency_amount = fields.ForeignKeyField("main.CurrencyAmount")

    converters = {
        ShortcutableType.item: "item",
        ShortcutableType.stat: "stat",
        ShortcutableType.role: "role",
        ShortcutableType.currency: "currency",
        ShortcutableType.inventory: "inventory",
        ShortcutableType.currency_amount: "currency_amount",
    }

    async def get(self) -> StuffShortcutable:
        """|coro|

        Returns the shortcut's model.

        Returns
        --------
        :class:`~taho.abc.StuffShortcutable`
            The shortcut's model.
        """
        return await super().get()

class AccessShortcut(Shortcut):
    """Represents a shortcut to a
    :class:`~taho.abc.AccessShortcutable` model. 
    
    See :ref:`Shortcuts <shortcut>` for more information.
    """
    class Meta:
        table = "shortcuts_access"

    user = fields.ForeignKeyField("main.User")
    role = fields.ForeignKeyField("main.Role")

    converters = {
        ShortcutableType.user: "user",
        ShortcutableType.role: "role",
    }

    async def get(self) -> AccessShortcutable:
        """|coro|

        Returns the shortcut's model.

        Returns
        --------
        :class:`~taho.abc.AccessShortcutable`
            The shortcut's model.
        """
        return await super().get()

class TradeStuffShortcut(Shortcut):
    """Represents a shortcut to a
    :class:`~taho.abc.TradeStuffShortcutable` model. 
    
    See :ref:`Shortcuts <shortcut>` for more information.
    """
    class Meta:
        table = "shortcuts_trade_stuff"

    inventory = fields.ForeignKeyField("main.Inventory")
    currency_amount = fields.ForeignKeyField("main.CurrencyAmount")

    converters = {
        ShortcutableType.inventory: "inventory",
        ShortcutableType.currency_amount: "currency_amount",
    }

    async def get(self) -> TradeStuffShortcutable:
        """|coro|

        Returns the shortcut's model.

        Returns
        --------
        :class:`~taho.abc.TradeStuffShortcutable`
            The shortcut's model.
        """
        return await super().get()