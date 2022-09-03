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
from .reward import RewardPack, Reward
from taho.enums import RewardType
from .access_rule import AccessRule

if TYPE_CHECKING:
    from typing import List, Dict

__all__ = (
    "Craft",
    "CraftRewardPack",
    "CraftReward",
    "CraftHistory",
    "CraftAccessRule",
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
        
        .. collapse:: emoji

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
                - :attr:`null` ``True``
            
            Python: Optional[:class:`str`]
        
        .. collapse:: description

            Tortoise: :class:`tortoise.fields.TextField`

                - :attr:`null` ``True``
            
            Python: Optional[:class:`str`]


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
        
    Attributes
    -----------
    id: :class:`int`
        The craft's ID.
    name: :class:`str`
        The craft's name.
    emoji: Optional[:class:`~taho.Emoji`]
        The craft's emoji.
    description: Optional[:class:`str`]
        The craft's description.
    cluster: :class:`~taho.database.models.Cluster`
        The cluster where the craft is.
    time: :class:`int`
        How many times the craft can be done before 
        it's cooldown.
    per: :class:`int`
        How many times the craft can be done per
        day.


    .. note:: 

        Cooldown explanation:

            - x = time
            - y = per
        
        For an infinite cooldown, set ``x`` to ``-1`` and ``y`` to ``0``.
        
        The craft can be done x times every y seconds.
    """
    class Meta:
        table = "crafts"
    
    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.Cluster", related_name="crafts")
    name = fields.CharField(max_length=255)
    emoji = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)
    time = fields.IntField()
    per = fields.IntField()

    access_rules: fields.ReverseRelation["CraftAccessRule"]
    reward_packs: fields.ReverseRelation["CraftRewardPack"]

    def __str__(self) -> str:
        return self.get_display()
    
    def get_display(self) -> str:
        """
        Returns the craft's display.

        Returns
        -------
        :class:`str`
            The craft's display.
        """
        return f"**{self.emoji} {self.name}**" if self.emoji else f"**{self.name}**"

    async def get_rewards(self) -> Dict[float, List[CraftReward]]:
        """
        |coro|
        
        Returns the craft's rewards.
        
        Returns
        -------
        :class:`dict`
            The craft's rewards.
        

        .. note::

            The returned dictionary is of the form::

                {
                    probability: [
                        CraftReward(),
                        ...
                    ],
                    ...
                }
        
        """
        from taho.utils import RandomHash

        rewards = {}
        async for _rewards in self.reward_packs.all().prefetch_related('rewards'):

            reward_list = await _rewards.rewards.all().prefetch_related("stuff_shortcut")
            rewards[_rewards.type][RandomHash(_rewards.luck)] = reward_list
        
        return rewards
    

class CraftRewardPack(RewardPack):
    """
    Represents a reward pack for a craft.

    .. container:: operations

        .. describe:: x == y

            Checks if two reward packs are equal.

        .. describe:: x != y

            Checks if two reward packs are not equal.
        
        .. describe:: hash(x)

            Returns the reward pack's hash.
        
        .. describe:: str(x)

            Returns the reward pack's name.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: craft

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Craft`
                - :attr:`related_name` ``reward_packs``
            
            Python: :class:`~taho.database.models.Craft`
        
        .. collapse:: type

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.RewardType`
                - :attr:`null` ``True``
            
            Python: Optional[:class:`~taho.enums.RewardType`]
        
        .. collapse:: luck

            Tortoise: :class:`tortoise.fields.DecimalField`

                - :attr:`max_digits` ``1``
                - :attr:`decimal_places` ``4``
                - :attr:`default` 1
            
            Python: :class:`float`
    
    Attributes
    -----------
    id: :class:`int`
        The reward pack's ID.
    craft: :class:`.Craft`
        |coro_attr|

        The reward pack's craft.
    type: :class:`~taho.enums.RewardType`
        The craft reward's type.
    luck: :class:`float`
        The reward pack's luck.
    rewards: List[:class:`.CraftReward`]
        |coro_attr|

        The rewards included in the reward pack.
    """
    class Meta:
        table = "craft_reward_packs"
    

    craft = fields.ForeignKeyField('main.Craft', related_name='reward_packs')

    type = fields.IntEnumField(RewardType, null=True)

    rewards: fields.ReverseRelation["CraftReward"]

class CraftReward(Reward):
    """
    Represents a craft reward.

    .. container:: operations

        .. describe:: x == y

            Checks if two craft rewards are equal.

        .. describe:: x != y

            Checks if two craft rewards are not equal.
        
        .. describe:: hash(x)

            Returns the craft reward's hash.
        
        .. describe:: str(x)

            Returns the craft reward's name.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: pack

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.CraftRewardPack`
                - :attr:`related_name` ``rewards``
            
            Python: :class:`~taho.database.models.CraftRewardPack`
        
        .. collapse:: stuff_shortcut

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.StuffShortcut`
            
            Python: :class:`~taho.database.models.StuffShortcut`
        
        .. collapse:: regeneration

            Tortoise: :class:`tortoise.fields.BooleanField`

                - :attr:`default` ``False``
            
            Python: :class:`bool`
        
        .. collapse:: durability

            Tortoise: :class:`tortoise.fields.BooleanField`

                - :attr:`default` ``False``
            
            Python: :class:`bool`
        
        .. collapse:: amount

            Tortoise: :class:`tortoise.fields.DecimalField`

                - :attr:`default` ``1``
                - :attr:`max_digits` ``10``
                - :attr:`decimal_places` ``2``
            
            Python: :class:`float`

    Attributes
    -----------
    id: :class:`int`
        The craft reward's ID.
    pack: :class:`~taho.database.models.CraftRewardPack`
        The craft reward's pack.
    stuff_shortcut: :class:`~taho.database.models.StuffShortcut`
        The craft reward's shortcut.
    regeneration: :class:`bool`
        If the shortcut points to a :class:`~taho.database.models.Stat`,
        then this is whether the stat should be regenerated.
    durability: :class:`bool`
        If the shortcut points to a :class:`~taho.database.models.Craft`,
        then this is whether it should add durability to it.
    amount: :class:`float`
        The amount of the reward.
    """
    class Meta:
        table = "craft_rewards"
    
    pack = fields.ForeignKeyField("main.CraftRewardPack", related_name="rewards")

class CraftAccessRule(AccessRule):
    """Represents an access rule to a craft.

    .. container:: operations

        .. describe:: x == y

            Checks if two rules are equal.

        .. describe:: x != y

            Checks if two rules are not equal.
        
        .. describe:: hash(x)

            Returns the rule's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
            
        .. collapse:: craft

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Craft`
                - :attr:`related_name` ``access_rules``
            
            Python: :class:`~taho.database.models.Craft`
        
        .. collapse:: have_access

            Tortoise: :class:`tortoise.fields.BooleanField`

            Python: :class:`bool`
        
        .. collapse:: access_shortcut

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.AccessRuleShortcut`
            
            Python: :class:`~taho.database.models.StuffShortcut`
        
    Attributes
    -----------
    id: :class:`int`
        The craft access's ID.
    craft: :class:`~taho.database.models.Craft`
        |coro_attr|

        The craft linked to this access.
    have_access: :class:`bool`
        Whether the user/role has access to the craft.
    access_shortcut: :class:`~taho.database.models.AccessRuleShortcut`
        |coro_attr|
        
        The shortcut to the entity which has access to the craft.
    """
    class Meta:
        table = "craft_access_rules"
    
    id = fields.IntField(pk=True)

    craft = fields.ForeignKeyField("main.Craft", related_name="access_rules")

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
        
        .. collapse:: amount

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`default` ``1``
            
            Python: :class:`int`
        
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
    amount: :class:`int`
        The amount of the craft done.
    done_at: :class:`datetime.datetime`
        When the craft was done.
    """
    class Meta:
        table = "craft_history"
    
    id = fields.IntField(pk=True)

    craft = fields.ForeignKeyField("main.Craft", related_name="craft_history")
    user = fields.ForeignKeyField("main.User", related_name="craft_history")
    amount = fields.IntField(default=1)
    done_at = fields.DatetimeField(auto_now_add=True)

