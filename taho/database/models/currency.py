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
from taho.abc import StuffShortcutable, TradeStuffShortcutable
from taho.currency_amount import CurrencyAmount as _CurrencyAmount

if TYPE_CHECKING:
    from .item import Item


__all__ = (
    "Currency",
    "CurrencyAmount",
)

class Currency(BaseModel, StuffShortcutable):
    """|shortcutable|
    
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
        
        .. collapse:: emoji

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
                - :attr:`null` ``True``
            
            Python: Optional[:class:`str`]
        
        .. collapse:: exchange_rate

            Tortoise: :class:`tortoise.fields.DecimalField`

                - :attr:`max_digits` 20
                - :attr:`decimal_places` 10
                - :attr:`default` 1.0
            
            Python: :class:`float`
        
        .. collapse:: is_default

            Tortoise: :class:`tortoise.fields.BooleanField`

                - :attr:`default` False

            Python: :class:`bool`

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
    emoji: Optional[:class:`~taho.emoji.Emoji`]
        The currency's emoji.
    exchange_rate: :class:`float`
        The currency's exchange_rate.
        It is used to convert one currency to another.

        .. warning::

            Please avoid setting the exchange_rate to 0, 
            as this will cause a division by zero.
    is_default: :class:`bool`
        Whether the currency is the default one.
    currency: Optional[:class:`~taho.database.models.Item`]
        |coro_attr|

        The currency's currency.
        Used to be the Cash of this currency.
    """
    class Meta:
        table = "currencies"
    
    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.Cluster", related_name="currencies")
    name = fields.CharField(max_length=255)
    symbol = fields.CharField(max_length=255)
    code = fields.CharField(max_length=255, null=True)
    emoji = fields.CharField(max_length=255, null=True)
    exchange_rate = fields.DecimalField(max_digits=20, decimal_places=10, default=1)
    is_default = fields.BooleanField(default=False)

    item: fields.OneToOneNullableRelation["Item"]

    def __str__(self) -> str:
        return self.get_display()
    
    def get_display(self) -> str:
        """
        Returns the currency's display.
        
        Returns
        -------
        :class:`str`
            The currency's display.
        """
        if self.code:
            return f"{self.emoji} {self.code}" if self.emoji else self.code
        else:
            return f"{self.emoji} {self.name}" if self.emoji else self.name

    
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
    

class CurrencyAmount(BaseModel, StuffShortcutable, TradeStuffShortcutable, _CurrencyAmount):
    """|shortcutable|
    
    Represents an amount of a currency.

    .. container:: operations

        .. describe:: x == y

            Checks if two amounts are equal.
        
        .. describe:: x != y

            Checks if two amounts are not equal.
        
        .. describe:: hash(x)

            Returns the hash of a amount.
        
    .. container:: fields

        .. collapse:: id

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: amount

            Tortoise: :class:`tortoise.fields.DecimalField`

                - :attr:`max_digits` 32
                - :attr:`decimal_places` 2
            
            Python: :class:`float`
        
        .. collapse:: currency

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`.Currency`

            Python: :class:`.Currency`
    
    Attributes
    ----------
    id: :class:`int`
        The currency amount's ID (DB primary key).
    amount: :class:`float`
        The amount.
    currency: :class:`.Currency`
        The currency in which the amount is.
    """
    class Meta:
        table = "currency_amounts"
    
    id = fields.IntField(pk=True)

    amount = fields.DecimalField(max_digits=32, decimal_places=2)
    currency = fields.ForeignKeyField("main.Currency")

    async def credit(self, amount: float) -> None:
        """|coro|
        
        Adds an amount to the currency amount.
        
        Parameters
        ----------
        amount: :class:`float`
            The amount to add.
        """
        await super().credit(amount)
        await self.save()