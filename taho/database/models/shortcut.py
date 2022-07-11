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
from tortoise.models import Model
from tortoise import fields
from taho.enums import ShortcutType

if TYPE_CHECKING:
    from .item import Item
    from .stat import Stat
    from .currency import Currency
    from typing import Union

__all__ = (
    "Shortcut",
)

class Shortcut(Model):
    """Represents a shortcut to:
    - an :class:`~taho.database.models.Item`;
    - a :class:`~taho.database.models.Stat`;
    - a :class:`~taho.database.models.Currency`.

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
    """
    class Meta:
        table = "shortcuts"
    
    id = fields.IntField(pk=True)
    type = fields.IntEnumField(ShortcutType, default=ShortcutType.item)
    item = fields.ForeignKeyField("main.Item", related_name="shortcuts", null=True)
    stat = fields.ForeignKeyField("main.Stat", related_name="shortcuts", null=True)
    currency = fields.ForeignKeyField("main.Currency", related_name="shortcuts", null=True)

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return super().__repr__()
    
    def __hash__(self) -> int:
        return hash(self.__repr__())
    
    async def get(self) -> Union[Item, Stat, Currency]:
        """|coro|

        Returns the shortcut's item, stat, or currency.

        Returns
        --------
        Union[
            :class:`~taho.database.models.Item`, 
            :class:`~taho.database.models.Stat`, 
            :class:`~taho.database.models.Currency`
            ]
            THe shortcut's item, stat, or currency.
        """
        converters = {
            ShortcutType.item: self.item,
            ShortcutType.stat: self.stat,
            ShortcutType.currency: self.currency,
        }
        return converters[self.type] #todo check if |coro_attr|
