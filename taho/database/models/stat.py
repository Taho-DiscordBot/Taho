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
from taho.enums import RPEffect, RegenerationType
from taho.abc import StuffShortcutable

if TYPE_CHECKING:
    from taho import Emoji, Bot

__all__ = (
    "Stat",
)

class Stat(BaseModel, StuffShortcutable):
    """|shortcutable|
    
    Represents a Statistic.

    .. container:: operations

        .. describe:: x == y

            Checks if two stats are equal.

        .. describe:: x != y

            Checks if two stats are not equal.
        
        .. describe:: hash(x)

            Returns the stat's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: cluster

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Cluster`
                - :attr:`related_name` ``cluster``
            
            Python: :class:`~taho.database.models.Cluster`

        .. collapse:: name

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``

            Python: :class:`str`
        
        .. collapse:: emoji

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
                - :attr:`null` True
            
            Python: Optional[:class:`str`]
        
        .. collapse:: rp_effect

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.RPEffect`
                - :attr:`null` True
            
            Python: Optional[:class:`~taho.enums.RPEffect`]
        
        .. collapse:: maximum

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`null` True
            
            Python: Optional[:class:`int`]
        
        .. collapse:: regeneration

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.RegenerationType`
                - :attr:`default` :attr:`~taho.enums.RegenerationType.no_regeneration`
            
            Python: :class:`~taho.enums.RegenerationType`
        
        .. collapse:: duration

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`null` True
            
            Python: Optional[:class:`int`]
        
    Attributes
    -----------
    id: :class:`int`
        The stat's ID.
    cluster: :class:`~taho.database.models.Cluster`
        The cluster the stat belongs to.
    name: :class:`str`
        The stat's name.
    emoji: Optional[:class:`~taho.Emoji`]
        The stat's emoji.
    rp_effect: Optional[:class:`~taho.enums.RPEffect`]
        The stat's RP effect.
    maximum: Optional[:class:`int`]
        The stat's maximum value.
    regeneration: :class:`~taho.enums.RegenerationType`
        The stat's regeneration type.
    duration: Optional[:class:`int`]
        The stat's duration.
    """
    class Meta:
        table = "stats"

    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.Cluster", related_name="stats")
    name = fields.CharField(max_length=255)
    emoji = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)
    rp_effect = fields.IntEnumField(RPEffect, null=True)
    maximum = fields.IntField(null=True)
    regeneration = fields.IntEnumField(RegenerationType, default=RegenerationType.no_regeneration)
    duration = fields.IntField(null=True)



    def get_emoji(self, bot: Bot) -> Emoji:
        """
        Get the stat's emoji as a :class:`~taho.Emoji` object.

        Parameters
        ----------
        bot: :class:`~taho.Bot`
            The bot instance.
            Used to get the emoji from Discord.
        
        Returns
        --------
        :class:`~taho.Emoji`
            The stat's emoji.
        """
        from taho import Emoji
        return Emoji(self.emoji, bot=bot)