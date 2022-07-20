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
from typing import TYPE_CHECKING
from tortoise import fields

if TYPE_CHECKING:
    from taho.abc import StuffShortcutable

__all__ = (
    "Craft",
    "CraftCost",
    "CraftReward",
    "CraftAccess",
    "CraftHistory",
)

class Craft(BaseModel):
    """Represents a craft.

    .. container:: operations

        .. describe:: x == y

            Checks if two crafts are equal.

        .. describe:: x != y

            Checks if two crafts are not equal.
        
        .. describe:: hash(x)

            Returns the craft's hash.
        
        .. describe:: str(x)

            Returns the craft's name.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: name

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
            
            Python: :class:`str`

        .. collapse:: cluster

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Cluster`
                - :attr:`related_name` ``crafts``
            
            Python: :class:`~taho.database.models.Cluster`
        
        .. collapse:: time

            Tortoise: :class:`tortoise.fields.IntField`

            Python: Optional[:class:`int`]
        
        ... collapse:: per

            Tortoise: :class:`tortoise.fields.IntField`

            Python: Optional[:class:`int`]
        
        .. collapse:: success

            Tortoise: :class:`tortoise.fields.DecimalField`

                - :attr:`max_digits` 32
                - :attr:`decimal_places` 2
            
            Python: :class:`float`
        
    Attributes
    -----------
    id: :class:`int`
        The craft's ID.
    name: :class:`str`
        The craft's name.
    cluster: :class:`~taho.database.models.Cluster`
        The cluster where the craft is.
    time: :class:`int`
        How many times the craft can be done before 
        it's cooldown.
    per: :class:`int`
        How many times the craft can be done per
        day.
    success: :class:`float`
        The chance of success (0.0 - 1.0).
    

    .. note:: 

        Cooldown explanation:

            - x = time
            - y = per
        
        The craft can be done x times every y seconds.
    """
    class Meta:
        table = "crafts"
    
    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.Cluster", related_name="crafts")
    name = fields.CharField(max_length=255)
    time = fields.IntField()
    per = fields.IntField()
    success = fields.DecimalField(max_digits=32, decimal_places=2, null=True)

    rewards: fields.ReverseRelation["CraftReward"]
    costs: fields.ReverseRelation["CraftCost"]



class CraftReward(BaseModel):
    """Represents a reward for a craft.

    .. container:: operations

        .. describe:: x == y

            Checks if two rewards are equal.

        .. describe:: x != y

            Checks if two rewards are not equal.
        
        .. describe:: hash(x)

            Returns the reward's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
            
        .. collapse:: craft

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Craft`
                - :attr:`related_name` ``rewards``
            
            Python: :class:`~taho.database.models.Craft`
        
        .. collapse:: stuff_shortcut

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.StuffShortcut`
                - :attr:`related_name` ``craft_rewards``
            
            Python: :class:`~taho.database.models.StuffShortcut`

        .. collapse:: give_regeneration

            Tortoise: :class:`tortoise.fields.BooleanField`

                - :attr:`null` True
            
            Python: Optional[:class:`bool`]
        
        .. collapse:: amount

            Tortoise: :class:`tortoise.fields.IntField`

            Python: :class:`int`    

    Attributes
    -----------
    id: :class:`int`
        The reward's ID.
    craft: :class:`~taho.database.models.Craft`
        The craft linked to the reward.
    stuff_shortcut: :class:`~taho.database.models.StuffShortcut`
        A shortcut to the reward (item, stat or currency).
    give_regeneration: Optional[:class:`bool`]
        If the reward is a :class:`~taho.database.models.Stat`, then a regenerable point
        will be rewarded.
    amount: :class:`int`
        The amount rewarded.
    

    .. note::

        In this model, the :attr:`.CraftReward.stuff_shortcut` is
        an :class:`~taho.database.models.StuffShortcut` that
        point to a :class:`~taho.abc.StuffShortcutable` model.

        See :ref:`Shortcuts <shortcut>` for more information.
    """
    class Meta:
        table = "craft_rewards"
    
    id = fields.IntField(pk=True)

    craft = fields.ForeignKeyField("main.Craft", related_name="rewards")
    stuff_shortcut = fields.ForeignKeyField("main.StuffShortcut")
    give_regeneration = fields.BooleanField(null=True)
    amount = fields.IntField()
    
    async def get_reward(self) -> StuffShortcutable:
        """|coro|

        Get the real reward from the :attr:`.CraftReward.stuff_shortcut`.

        Returns
        --------
        :class:`~taho.abc.StuffShortcutable`
            The shortcut's item, stat, or currency.
        """
        return await self.stuff_shortcut

class CraftCost(BaseModel):
    """Represents a cost for a craft.

    .. container:: operations

        .. describe:: x == y

            Checks if two costs are equal.

        .. describe:: x != y

            Checks if two costs are not equal.
        
        .. describe:: hash(x)

            Returns the cost's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
            
        .. collapse:: craft

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Craft`
                - :attr:`related_name` ``costs``
            
            Python: :class:`~taho.database.models.Craft`
        
        .. collapse:: stuff_shortcut

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.StuffShortcut`
                - :attr:`related_name` ``craft_costs``
            
            Python: :class:`~taho.database.models.StuffShortcut`
        
        .. collapse:: use_durabilty

            Tortoise: :class:`tortoise.fields.BooleanField`

                - :attr:`null` True
            
            Python: Optional[:class:`bool`]
        
        .. collapse:: use_regeneration

            Tortoise: :class:`tortoise.fields.BooleanField`

                - :attr:`null` True
            
            Python: Optional[:class:`bool`]
        
        .. collapse:: amount

            Tortoise: :class:`tortoise.fields.IntField`

            Python: :class:`int`    

    Attributes
    -----------
    id: :class:`int`
        The cost's ID.
    craft: :class:`~taho.database.models.Craft`
        The craft linked to the cost.
    stuff_shortcut: :class:`~taho.database.models.StuffShortcut`
        A shortcut to the cost (item, stat, ...).
    use_durabilty: Optional[:class:`bool`]
        If the cost is a :class:`~taho.database.models.Item`, then durability will be
        removed to the item.
    use_regeneration: Optional[:class:`bool`]
        If the cost is a :class:`~taho.database.models.Stat`, then regenerable points
        will be removed.
    amount: :class:`int`
        The amount costed.
    

    .. note::

        In this model, the :attr:`.CraftCost.stuff_shortcut` is
        an :class:`~taho.database.models.StuffShortcut` that
        point to a :class:`~taho.abc.StuffShortcutable` model.

        See :ref:`Shortcuts <shortcut>` for more information.
    """
    class Meta:
        table = "craft_costs"
    
    id = fields.IntField(pk=True)

    craft = fields.ForeignKeyField("main.Craft", related_name="costs")
    stuff_shortcut = fields.ForeignKeyField("main.StuffShortcut")
    use_durability = fields.BooleanField(null=True)
    use_regeneration = fields.BooleanField(null=True)
    amount = fields.IntField()
    
    async def get_cost(self) -> StuffShortcutable:
        """|coro|

        Get the real cost from the :attr:`.CraftCost.stuff_shortcut`

        Returns
        --------
        :class:`~taho.abc.StuffShortcutable`
            The shortcut's item, stat, or currency.
        """
        return await self.stuff_shortcut

class CraftHistory(BaseModel):
    """Represents a craft done by a user.

    .. container:: operations

        .. describe:: x == y

            Checks if two crafts are equal.

        .. describe:: x != y

            Checks if two crafts are not equal.
        
        .. describe:: hash(x)

            Returns the craft's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
            
        .. collapse:: craft

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Craft`
                - :attr:`related_name` ``history``
            
            Python: :class:`~taho.database.models.Craft`
        
        .. collapse:: user

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.User`
                - :attr:`related_name` ``craft_history``
            
            Python: :class:`~taho.database.models.User`
        
        .. collapse:: done_at

            Tortoise: :class:`tortoise.fields.DatetimeField`

                - :attr:`auto_now_add` ``True``
            
            Python: :class:`datetime.datetime`
        
    Attributes
    -----------
    id: :class:`int`
        The craft's ID.
    craft: :class:`~taho.database.models.Craft`
        The craft done.
    user: :class:`~taho.database.models.User`
        The user who did the craft.
    done_at: :class:`datetime.datetime`
        When the craft was done.
    """
    class Meta:
        table = "craft_history"
    
    id = fields.IntField(pk=True)

    craft = fields.ForeignKeyField("main.Craft", related_name="craft_history")
    user = fields.ForeignKeyField("main.User", related_name="craft_history")
    done_at = fields.DatetimeField(auto_now_add=True)

class CraftAccess(BaseModel):
    """Represents an access to a craft.

    .. container:: operations

        .. describe:: x == y

            Checks if two craft accesses are equal.

        .. describe:: x != y

            Checks if two craft accesses are not equal.
        
        .. describe:: hash(x)

            Returns the craft access's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
            
        .. collapse:: craft

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Craft`
                - :attr:`related_name` ``accesses``
            
            Python: :class:`~taho.database.models.Craft`
        
        .. collapse:: have_access

            Tortoise: :class:`tortoise.fields.BooleanField`

            Python: :class:`bool`
        
        .. collapse:: stuff_shortcut

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.StuffShortcut`
                - :attr:`related_name` ``craft_accesses``
            
            Python: :class:`~taho.database.models.StuffShortcut`
        
    Attributes
    -----------
    id: :class:`int`
        The craft access's ID.
    craft: :class:`~taho.database.models.Craft`
        The craft linked to this access.
    have_access: :class:`bool`
        Whether the user/role has access to the craft.
    stuff_shortcut: :class:`~taho.database.models.StuffShortcut`
        The shortcut to the :class:`~taho.database.models.User`
        or :class:`~taho.database.models.Role` who has access 
        to the craft.


    .. note::

        In this model, the :attr:`.CraftAccess.stuff_shortcut` is
        an :class:`~taho.database.models.AccessShortcut` that
        point to a :class:`~taho.abc.AccessShortcutable` model.

        See :ref:`Shortcuts <shortcut>` for more information.
    """
    class Meta:
        table = "craft_access"
    
    id = fields.IntField(pk=True)

    craft = fields.ForeignKeyField("main.Craft", related_name="accesses")
    have_access = fields.BooleanField()
    stuff_shortcut = fields.ForeignKeyField("main.AccessShortcut")
