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

if TYPE_CHECKING:
    from taho.database.models import Currency

__all__ = (
    "CurrencyAmount",
)

class CurrencyAmount:
    """
    Represents an amount of money in a specific currency.

    .. container:: operations

        .. describe:: x == y

            Checks if two currency amounts are equal.
            If y is a float, it will be compared to :attr:`amount`.
        
        .. describe:: x != y

            Checks if two currency amounts are not equal.
            If y is a float, it will be compared to :attr:`amount`.
        
        .. describe:: x < y

            Checks if the currency amount is less than y's.
            If y is a float, it will be compared to :attr:`amount`.
        
        .. describe:: x <= y

            Checks if the currency amount is less than or equal to y's.
            If y is a float, it will be compared to :attr:`amount`.
        
        .. describe:: x > y

            Checks if the currency amount is greater than y's.
            If y is a float, it will be compared to :attr:`amount`.
        
        .. describe:: hash(x)

            Returns the hash value for the currency amount.
        
    Attributes
    -----------
    amount: float
        The amount of money.
    currency: :class:`~taho.database.models.Currency`
        The currency of the money.
    """
    __slots__ = (
        "amount",
        "currency",
    )

    def __init__(self, amount: float, currency: Currency) -> None:
        self.amount = amount
        self.currency = currency
        self._conversions = {}
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, float):
            return self.amount == other
        return other.ammount == self.amount and other.currency == self.currency
    
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
    
    def __lt__(self, other: object) -> bool:
        if isinstance(other, float):
            return self.amount < other
        return self.amount < other.amount
    
    def __le__(self, other: object) -> bool:
        return self.__lt__(other) or self.__eq__(other)
    
    def __gt__(self, other: object) -> bool:
        if isinstance(other, float):
            return self.amount > other
        return self.amount > other.amount
    
    def __ge__(self, other: object) -> bool:
        return self.__gt__(other) or self.__eq__(other)
    
    def __hash__(self) -> int:
        return hash((self.amount, self.currency.__repr__()))
    
    async def convert(self, currency: Currency) -> float:
        """|coro|

        Convert the currency amount to the given currency.

        Parameters
        -----------
        currency: :class:`~taho.database.models.Currency`
            The currency to convert to.
        
        Returns
        --------
        float
            The converted amount.
        
        """
        if currency == self.currency: # no conversion needed
            return self.amount
        if not hasattr(self, "_conversions"):
            self._conversions = {} # prevent case where this class is parent of
            # the CurrencyAmount model (in which self.__init__ is not called)
        if currency not in self._conversions: # no conversion yet
            # convert from the current currency to the given currency
            # and store the result in the conversions dict
            self._conversions[currency] = await self.currency.convert(currency, self.amount)
        return self._conversions[currency] # return the converted amount
    
    async def credit(self, amount: float) -> None:
        """

        Add the given amount to the currency amount.

        Parameters
        -----------
        amount: float
            The amount to add.
        """
        self.amount += amount

    def clone(self, opposite: bool=False) -> CurrencyAmount:
        """

        Clone the currency amount.

        Parameters
        -----------
        opposite: bool
            If ``True``, the amount will be multiplied by -1.
            All conversions will be inverted.
        
        Returns
        --------
        :class:`~taho.utils.CurrencyAmount`
            The cloned currency amount.
        """
        amount = self.amount if not opposite else -self.amount
        new = CurrencyAmount(amount, self.currency)
        if opposite:
            for currency, amount in self._conversions.items():
                new._conversions[currency] = -amount
        return new