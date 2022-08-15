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
from taho.utils.abstract import AbstractAccessRule


__all__ = (
    "AccessRule",
)

class AccessRule(BaseModel):
    """
    Represents an access rule.

    .. container:: operations

        .. describe:: x == y

            Checks if two rules are equal.

        .. describe:: x != y

            Checks if two rules are not equal.
        
        .. describe:: hash(x)

            Returns the rule's hash.
        
        .. describe:: str(x)

            Returns the rule's name.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: access_shortcut

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.AccessRuleShortcut`
            
            Python: :class:`~taho.database.models.AccessRuleShortcut`
        
        .. collapse:: have_access

            Tortoise: :class:`tortoise.fields.BooleanField`

            Python: :class:`bool`
    
    Attributes
    -----------
    id: :class:`int`
        The rule's ID.
    access_shortcut: :class:`~taho.database.models.AccessRuleShortcut`
        The rule's shortcut.
    have_access: :class:`bool`
        Whether the entity has access.
    """
    class Meta:
        abstract = True
    
    id = fields.IntField(pk=True)

    access_shortcut = fields.ForeignKeyField("main.AccessRuleShortcut")

    have_access = fields.BooleanField()

    async def to_abstract(self) -> AbstractAccessRule:
        """|coro|

        Returns the access rule as an abstract access rule.

        Returns
        --------
        :class:`~taho.utils.AbstractAccessRule`
            The abstract access rule.
        """
        return AbstractAccessRule(
            have_access=self.have_access,
            access=await self.access
        )
