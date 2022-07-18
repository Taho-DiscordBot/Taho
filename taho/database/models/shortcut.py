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
from taho.enums import ShortcutType

if TYPE_CHECKING:
    from taho.abc import Shortcutable

__all__ = (
    "Shortcut",
)

class Shortcut(BaseModel):
    """Represents a shortcut to:
    - :class:`~taho.database.models.Item`
    - :class:`~taho.database.models.Stat`
    - :class:`~taho.database.models.Currency`
    - :class:`~taho.database.models.User`
    - :class:`~taho.database.models.Role`

    .. container:: operations

        .. describe:: x == y

            Checks if two shortcuts are equal.

        .. describe:: x != y

            Checks if two shortcuts are not equal.
        
        .. describe:: hash(x)

            Returns the shortcut's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: type
            
            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.ShortcutType`

            Python: :class:`~taho.enums.ShortcutType`
        
        .. collapse:: item
            
            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Item`
                - :attr:`related_name` ``shortcuts``
                - :attr:`null` ``True``
            
            Python: Optional[:class:`~taho.database.models.Item`]
        
        .. collapse:: stat
            
            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Stat`
                - :attr:`related_name` ``shortcuts``
                - :attr:`null` ``True``
            
            Python: Optional[:class:`~taho.database.models.Stat`]
        
        .. collapse:: currency
            
            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Currency`
                - :attr:`related_name` ``shortcuts``
                - :attr:`null` ``True``
            
            Python: Optional[:class:`~taho.database.models.Currency`]
        
        .. collapse:: user
            
            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.User`
                - :attr:`related_name` ``shortcuts``
                - :attr:`null` ``True``
            
            Python: Optional[:class:`~taho.database.models.User`]
        
        .. collapse:: role
            
            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Role`
                - :attr:`related_name` ``shortcuts``
                - :attr:`null` ``True``
            
            Python: Optional[:class:`~taho.database.models.Role`]

    Attributes
    -----------
    id: :class:`int`
        The shortcut's ID.
    type: :class:`~taho.enums.ShortcutType`
        The shortcut's type.
    item: Optional[:class:`~taho.database.models.Item`]
        If the :attr:`.type` is :attr:`~taho.enums.ShortcutType.item`,
        this is the item.
    stat: Optional[:class:`~taho.database.models.Stat`]
        If the :attr:`.type` is :attr:`~taho.enums.ShortcutType.stat`,
        this is the stat.
    currency: Optional[:class:`~taho.database.models.Currency`]
        If the :attr:`.type` is :attr:`~taho.enums.ShortcutType.currency`,
        this is the currency.   
    user: Optional[:class:`~taho.database.models.User`]
        If the :attr:`.type` is :attr:`~taho.enums.ShortcutType.user`,
        this is the user.
    role: Optional[:class:`~taho.database.models.Role`]
        If the :attr:`.type` is :attr:`~taho.enums.ShortcutType.role`,
        this is the role.
    """
    class Meta:
        table = "shortcuts"
    
    id = fields.IntField(pk=True)
    type = fields.IntEnumField(ShortcutType, default=ShortcutType.item)
    item = fields.ForeignKeyField("main.Item", related_name="shortcuts", null=True)
    stat = fields.ForeignKeyField("main.Stat", related_name="shortcuts", null=True)
    currency = fields.ForeignKeyField("main.Currency", related_name="shortcuts", null=True)
    user = fields.ForeignKeyField("main.User", related_name="shortcuts", null=True)
    role = fields.ForeignKeyField("main.Role", related_name="shortcuts", null=True)



    
    async def get(self) -> Shortcutable:
        """|coro|

        Returns the shortcut's item, stat, or currency.

        Returns
        --------
        :class:`~taho.abc.Shortcutable`
            The shortcut's item, stat, or currency.
        """
        converters = {
            ShortcutType.item: self.item,
            ShortcutType.stat: self.stat,
            ShortcutType.currency: self.currency,
            ShortcutType.user: self.user,
            ShortcutType.role: self.role,
        }
        return converters[self.type] #todo check if |coro_attr|
