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

if TYPE_CHECKING:
    from typing import Optional
    from .cluster import Cluster
    from .role import Role

__all__ = (
    "Class",
    "ClassStat",
)

class Class(BaseModel):
    """Represents a class for a user.

    .. container:: operations

        .. describe:: x == y

            Checks if two classes are equal.

        .. describe:: x != y

            Checks if two classes are not equal.
        
        .. describe:: hash(x)

            Returns the class's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: cluster

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Cluster`
                - :attr:`related_name` ``classes``
                
            Python: :class:`~taho.database.models.Cluster`
        
        .. collapse:: name
            
            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
                
            Python: :class:`str`
        
        .. collapse:: emoji
            
            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
                - :attr:`null` ``True``

            Python: Optional[:class:`str`]
        
        .. collapse:: description

            Tortoise: :class:`tortoise.fields.TextField`

                - :attr:`null` ``True``
                
            Python: Optional[:class:`str`]
        
        .. collapse:: role

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Role`
                - :attr:`related_name` ``classes``
                
            Python: :class:`~taho.database.models.Role`

    Attributes
    -----------
    id: :class:`int`
        The class's ID.
    cluster: :class:`~taho.database.models.Cluster`
        The cluster the class belongs to.
    name: :class:`str`
        The class's name.
    emoji: Optional[:class:`~taho.Emoji`]
        The class's emoji.
    description: Optional[:class:`str`]
        The class's description.
    role: :class:`~taho.database.models.Role`
        The role linked to the class.
    stats: List[:class:`~taho.database.models.ClassStat`]
        |coro_attr|

        The stats added by the class.
    """
    id: int = fields.IntField(pk=True)
    cluster: Cluster = fields.ForeignKeyField("main.Cluster", related_name="classes")
    name: str = fields.CharField(max_length=255)
    emoji: Optional[str] = fields.CharField(max_length=255, null=True)
    description: Optional[str] = fields.TextField(null=True)
    role: Role = fields.ForeignKeyField("main.Role", related_name="classes")

    stats: fields.ReverseRelation["ClassStat"]

    def __str__(self) -> str:
        return self.name


    

class ClassStat(BaseModel):
    """Represents a stat of a class.

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
        
        .. collapse:: class_

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Class`
                - :attr:`related_name` ``stats``
                
            Python: :class:`~taho.database.models.Class`
        
        .. collapse:: stat

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Stat`
                - :attr:`related_name` ``classes``

            Python: :class:`~taho.database.models.Stat`
        
        .. collapse:: value

            Tortoise: :class:`tortoise.fields.IntField`

            Python: :class:`int`

    Attributes
    -----------
    id: :class:`int`
        The stat's ID.
    class: :class:`~taho.database.models.Class`
        The class the stat belongs to.
    stat: :class:`str`
        The stat's name.
    value: :class:`int`
        The amount of stat added by the class.
    """
    class Meta:
        table = "class_stats"

    id: int = fields.IntField(pk=True)
    class_: Class = fields.ForeignKeyField("main.Class", related_name="stats")
    stat: str = fields.ForeignKeyField("main.Stat", related_name="classes")
    value: int = fields.IntField()

