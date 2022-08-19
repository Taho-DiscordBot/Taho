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
from taho.enums import ShopType

if TYPE_CHECKING:
    from taho.abc import StuffShortcutable
    from typing import Union

__all__ = (
    "Shop",
    "Sale",
)

class Shop(BaseModel):
    """Represents a shop.

    .. container:: operations

        .. describe:: x == y

            Checks if two shops are equal.

        .. describe:: x != y

            Checks if two shops are not equal.
        
        .. describe:: hash(x)

            Returns the shop's hash.
        
        .. describe:: str(x)

            Returns the shop's name
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: cluster

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Cluster`
                - :attr:`related_name` ``shops``
            
            Python: :class:`taho.database.models.Cluster`
        
        .. collapse:: owner_shortcut

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.OwnerShortcut`
            
            Python: :class:`~taho.database.models.OwnerShortcut`
        
        .. collapse:: short_id

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`unique` ``True``
            
            Python: :class:`int`
        
        .. collapse:: type

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.ShopType`

            Python: :class:`~taho.enums.ShopType`
        
        .. collapse:: name

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``32``
            
            Python: :class:`str`
        
        .. collapse:: description

            Tortoise: :class:`tortoise.fields.TextField`

                - :attr:`null` ``True``
            
            Python: Optional[:class:`str`]
        
        .. collapse:: icon_url

            Tortoise: :class:`tortoise.fields.TextField`

                - :attr:`null` ``True``
            
            Python: Optional[:class:`str`]

    Attributes
    -----------
    id: :class:`int`
        The shop's ID.
    cluster: :class:`taho.database.models.Cluster`
        The cluster the shop is in.
    owner_shortcut: :class:`taho.database.models.OwnerShortcut`
        The entity who owns the shop.
    short_id: :class:`int`
        The shop's short ID.
    type: :class:`taho.enums.ShopType`
        The shop's type.
    name: :class:`str`
        The shop's name.
    description: Optional[:class:`str`]
        The shop's description.
    icon_url: Optional[:class:`str`]
        The shop's icon URL.
    sales: List[:class:`.Sale`]
        |coro_attr|

        The shop's sales.
    

    .. note::

        In this model, the :attr:`.Shop.owner_shortcut` is
        an :class:`~taho.database.models.OwnerShortcut` that
        point to a :class:`~taho.abc.OwnerShortcutable` model.

        See :ref:`Shortcuts <shortcut>` for more information.
    """
    class Meta:
        table = "shops"

    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.Cluster", related_name="shops")
    owner_shortcut = fields.ForeignKeyField("main.OwnerShortcut")
    short_id = fields.IntField(unique=True)
    type = fields.IntEnumField(ShopType)
    name = fields.CharField(max_length=32)
    description = fields.TextField(null=True)
    icon_url = fields.TextField(null=True)

    sales: fields.ReverseRelation["Sale"]

class Sale(BaseModel):
    """Represents something from sale in a shop.

    .. container:: operations

        .. describe:: x == y

            Checks if two sales are equal.

        .. describe:: x != y

            Checks if two sales are not equal.
        
        .. describe:: hash(x)

            Returns the sale's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: shop

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Shop`
                - :attr:`related_name` ``sales``
            
            Python: :class:`taho.database.models.Shop`
        
        .. collapse:: stuff_shortcut

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.StuffShortcut`

            Python: :class:`~taho.database.models.StuffShortcut`
        
        .. collapse:: price

            Tortoise: :class:`tortoise.fields.DecimalField`

                - :attr:`max_digits` ``32``
                - :attr:`decimal_places` ``2``
            
            Python: :class:`float`
        
        .. collapse:: currency

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Currency`

            Python: :class:`~taho.database.models.Currency`
        
        .. collapse:: amount 

            Tortoise: :class:`tortoise.fields.IntField`

            Python: :class:`int`
        
        .. collapse:: description

            Tortoise: :class:`tortoise.fields.TextField`

                - :attr:`null` ``True``
            
            Python: Optional[:class:`str`]
        
        .. collapse:: end_time

            Tortoise: :class:`tortoise.fields.DatetimeField`

                - :attr:`null` ``True``
            
            Python: Optional[:class:`datetime.datetime`]

    Attributes
    -----------
    id: :class:`int`
        The sale's ID.
    shop: :class:`taho.database.models.Shop`
        The shop the sale is in.
    stuff_shortcut: :class:`taho.database.models.StuffShortcut`
        The stuff the sale is for.
    price: :class:`float`
        The sale's price.
    currency: :class:`taho.database.models.Currency`
        The sale price's currency.
    amount: Optional[:class:`int`]
        The amount of stuff the sale is for.
    description: Optional[:class:`str`]
        The sale's description.
    end_time: Optional[:class:`datetime.datetime`]
        The sale's end time.
    """
    class Meta:
        table = "shop_sales"
    
    id = fields.IntField(pk=True)

    shop = fields.ForeignKeyField("main.Shop", related_name="sales")
    owner_shortcut = fields.ForeignKeyField("main.OwnerShortcut")
    stuff_shortcut = fields.ForeignKeyField("main.StuffShortcut")
    price = fields.DecimalField(max_digits=32, decimal_places=2)
    currency = fields.ForeignKeyField("main.Currency")
    amount = fields.IntField()
    description = fields.TextField(null=True)
    end_time = fields.DatetimeField(null=True)

    
    async def get_stuff(self, force: bool = False) -> StuffShortcutable:
        from taho.database.db_utils import get_stuff # avoid circular import

        return await get_stuff(self, force=force)
    
    async def get_stuff_amount(self, force: bool = False) -> Union[float, int]:
        from taho.database.db_utils import get_stuff_amount # avoid circular import

        return await get_stuff_amount(self, force=force)
