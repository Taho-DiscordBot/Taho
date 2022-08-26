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
from taho.abstract import AbstractInfo
from ..db_utils import value_from_json

if TYPE_CHECKING:
    from typing import TypeVar

    T = TypeVar("T", None, bool, int, float, str)


__all__ = (
    "Info",
)

class Info(BaseModel):
    """
    Represents an info.

    .. container:: operations

        .. describe:: x == y

            Checks if two infos are equal.

        .. describe:: x != y

            Checks if two infos are not equal.
        
        .. describe:: hash(x)

            Returns the info's hash.
        
        .. describe:: str(x)

            Returns the info's name.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: key

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
            
            Python: :class:`str`
        
        .. collapse:: type

            Tortoise: :class:`tortoise.models.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.InfoType`
            
            Python: :class:`~taho.enums.InfoType`
        
        .. collapse:: value

            Tortoise: :class:`tortoise.models.fields.CharField`

                - :attr:`max_length` ``255``
            
            Python: :class:`str`
    
    Attributes
    -----------
    id: :class:`int`
        The info's ID.
    key: :class:`str`
        The info's key.
    type: :class:`~taho.enums.InfoType`
        The info's type.
        Used to convert the value to the correct
        python type.
    value: :class:`str`
        The info's value stored in the DB.
    py_value: Union[``None``, :class:`bool`, :class:`int`, :class:`float`, :class:`str`]
        The value of the info in Python's type.
    """
    class Meta:
        abstract = True
    
    id = fields.IntField(pk=True)

    key = fields.CharField(max_length=255)
    value = fields.JSONField()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        return other == self.value["value"]

    async def get_py_value(self) -> T:
        if hasattr(self, "_py_value"):
            return self._py_value
        
        self._py_value = await value_from_json(self.value, fetch=True, silent_error=True)
        return self._py_value

    async def to_abstract(self) -> AbstractInfo:
        """|coro|

        Returns the info as an abstract info.

        Returns
        --------
        :class:`~taho.utils.AbstractInfo`
            The abstract info.
        """
        return AbstractInfo(
            key=self.key,
            value=await self.get_py_value()
        )
