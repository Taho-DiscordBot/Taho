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
        
        .. collapse:: short_id

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`unique` ``True``
            
            Python: :class:`int`
        
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
    short_id: :class:`int`
        The shop's short ID.
    name: :class:`str`
        The shop's name.
    description: Optional[:class:`str`]
        The shop's description.
    icon_url: Optional[:class:`str`]
        The shop's icon URL.
    """
    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.Cluster", related_name="shops")
    #owner ?
    short_id = fields.IntField(unique=True)
    name = fields.CharField(max_length=32)
    description = fields.TextField(null=True)
    icon_url = fields.TextField(null=True)

class Sale(BaseModel):
    pass