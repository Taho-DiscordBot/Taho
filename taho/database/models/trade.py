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
from .base import BaseModel
from tortoise import fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

__all__ = (
    "Trade",
    "TradePartie",
    "TradeStuff",
)

class Trade(BaseModel):
    """Represents a trade between two entities (users, ...).

    .. container:: operations

        .. describe:: x == y

            Checks if two trades are equal.

        .. describe:: x != y

            Checks if two trades are not equal.
        
        .. describe:: hash(x)

            Returns the trade's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: cluster

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Cluster`
                - :attr:`related_name` ``trades``
            
            Python: :class:`taho.database.models.Cluster`
        
        .. collapse:: description

            Tortoise: :class:`tortoise.fields.TextField`

                - :attr:`null` ``True``
            
            Python: Optional[:class:`str`]
        
    Attributes
    -----------
    id: :class:`int`
        The trade's ID.
    cluster: :class:`~taho.database.Cluster`
        The cluster the trade belongs to.
    description: Optional[:class:`str`]
        The trade's description.
    parties: List[:class:`~taho.database.models.OwnerShortcut`]
        |coro_attr|

        The trade's parties.
    stuff: List[:class:`~taho.database.models.TradeStuff`]
        |coro_attr|

        The traded stuff between the
        two parties.
    """
    class Meta:
        table = "trades"
    
    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.Cluster", related_name="trades")
    description = fields.TextField(null=True)

    parties: fields.ReverseRelation["TradePartie"]
    stuff: fields.ReverseRelation["TradeStuff"]

class TradePartie(BaseModel):
    """Represents a trade partie.

    .. container:: operations

        .. describe:: x == y

            Checks if two parties are equal.

        .. describe:: x != y

            Checks if two parties are not equal.
        
        .. describe:: hash(x)

            Returns the partie's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: trade

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Trade`
                - :attr:`related_name` ``parties``
            
            Python: :class:`taho.database.models.Trade`
        
        .. collapse:: owner_shortcut

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.OwnerShortcut`
            
            Python: :class:`taho.database.models.OwnerShortcut`
    
    Attributes
    -----------
    id: :class:`int`
        The partie's ID.
    trade: :class:`~taho.database.models.Trade`
        The trade the partie belongs to.
    owner_shortcut: :class:`~taho.database.models.OwnerShortcut`
        The owner shortcut the partie belongs to.
    """
    class Meta:
        table = "trade_parties"
    
    id = fields.IntField(pk=True)

    trade = fields.ForeignKeyField("main.Trade", related_name="parties")
    owner_shortcut = fields.ForeignKeyField("main.OwnerShortcut")

class TradeStuff(BaseModel):
    """Represents a trade stuff.

    .. container:: operations

        .. describe:: x == y

            Checks if two stuff are equal.

        .. describe:: x != y

            Checks if two stuff are not equal.
        
        .. describe:: hash(x)

            Returns the stuff's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: trade

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Trade`
                - :attr:`related_name` ``stuff``
            
            Python: :class:`taho.database.models.Trade`
        
        .. collapse:: stuff_shortcut

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.StuffShortcut`
            
            Python: :class:`taho.database.models.StuffShortcut`
    
    Attributes
    -----------
    id: :class:`int`
        The stuff's ID.
    trade: :class:`~taho.database.models.Trade`
        The trade the stuff belongs to.
    stuff_shortcut: :class:`~taho.database.models.Stuff`
        The stuff the stuff belongs to.
    

    .. note::

        In this model, the :attr:`.TradeStuff.stuff_shortcut` is
        an :class:`~taho.database.models.TradeStuffShortcut` that
        point to a :class:`~taho.abc.TradeStuffShortcutable` model.

        See :ref:`Shortcuts <shortcut>` for more information.
    """
    class Meta:
        table = "trade_stuff"
    
    id = fields.IntField(pk=True)

    trade = fields.ForeignKeyField("main.Trade", related_name="stuff")
    stuff_shortcut = fields.ForeignKeyField("main.TradeStuffShortcut")