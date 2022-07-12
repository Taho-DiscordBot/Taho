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
from tortoise.models import Model
from tortoise import fields
from taho.abc import Shortcutable


__all__ = (
    "Currency",
)

class Currency(Model, Shortcutable):
    """
    Represents a currency.

    .. container:: operations

        .. describe:: x == y

            Checks if two currencies are equal.
        
        .. describe:: x != y

            Checks if two currencies are not equal.
        
        .. describe:: hash(x)

            Returns the hash of a currency.
        
        .. describe:: str(x)

            Returns the currency's name.
    
    .. container:: fields

        .. collapse:: id

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: name

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``

            Python: :class:`str`
        
        .. collapse:: symbol

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``

            Python: :class:`str`
        
        .. collapse:: code

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
            
            Python: :class:`str`
        
        .. collapse:: rate

            Tortoise: :class:`tortoise.fields.DecimalField`

                - :attr:`max_digits` 20
                - :attr:`decimal_places` 10
                - :attr:`default` 1.0
            
            Python: :class:`float`

    Attributes
    ----------
    id: :class:`int`
        The currency's ID (DB primary key).
    cluster: :class:`~taho.database.models.Cluster`
        |coro_attr|
        
        The currency's cluster.
    name: :class:`str`
        The currency's name.
        ex: 'Euro'
    symbol: :class:`str`
        The currency's symbol.
        ex: '€'
    code: :class:`str`
        The currency's code.
        ex: 'EUR'
    rate: :class:`float`
        The currency's rate.
        It is used to convert one currency to another.

        .. warning::

            Please avoid setting the rate to 0, 
            as this will cause a division by zero.
    """
    class Meta:
        table = "currencies"
    
    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.Cluster", related_name="currencies")
    name = fields.CharField(max_length=255)
    symbol = fields.CharField(max_length=255)
    code = fields.CharField(max_length=255, null=True)
    rate = fields.DecimalField(max_digits=20, decimal_places=10, default=1)

    def __repr__(self) -> str:
        return super().__repr__()
    
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)
    
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash(self.__repr__())
    
    def __str__(self) -> str:
        return self.name
    
    async def convert(self, currency: Currency, amount: float) -> float:
        """|coro|
        
        Converts an amount of one currency to another.
        The amount will be converted from this one
        to the one given.
        
        Parameters
        ----------
        currency: :class:`.Currency`
            The currency to convert to.
        amount: :class:`float`
            The amount of the currency to convert.
        
        Raises
        ------
        DivisionByZero
            If the currency's rate is 0.

        Returns
        -------
        :class:`float`
            The converted amount.
        """
        return amount * (self.rate / currency.rate)
    

