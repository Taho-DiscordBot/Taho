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
from tortoise.validators import MinValueValidator, MaxValueValidator

if TYPE_CHECKING:
    from taho.abc import StuffShortcutable
    from typing import Union, List, Dict

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

    accesses: fields.ReverseRelation["CraftAccessRule"]
    reward_packs: fields.ReverseRelation["CraftRewardPack"]

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
    
class CraftRewardPack(BaseModel):
    """
    Represents a reward pack for an craft.

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

                - :attr:`enum` :class:`~taho.enums.CraftRewardType`
            
            Python: :class:`~taho.enums.CraftRewardType`
        
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
    craft: :class:`~taho.database.models.Craft`
        |coro_attr|

        The reward pack's craft.
    type: :class:`~taho.enums.CraftRewardType`
        The craft reward's type.
    luck: :class:`float`
        The reward pack's luck.
    rewards: List[:class:`~taho.database.models.CraftReward`]
        |coro_attr|

        The rewards included in the reward pack.
    """
    class Meta:
        table = "craft_reward_packs"
    
    id = fields.IntField(pk=True)

    craft = fields.ForeignKeyField('main.Craft', related_name='reward_packs')

    luck = fields.FloatField(default=1, validators=[MinValueValidator(0), MaxValueValidator(1)])

    rewards: fields.ReverseRelation["CraftReward"]

class CraftReward(BaseModel):
    """
    Represents an craft reward.

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
    
    id = fields.IntField(pk=True)

    pack = fields.ForeignKeyField("main.CraftRewardPack", related_name="rewards")
    stuff_shortcut = fields.ForeignKeyField("main.StuffShortcut")
    regeneration = fields.BooleanField(default=False)
    durability = fields.BooleanField(default=False)
    amount = fields.DecimalField(max_digits=10, decimal_places=2, default=1)
    
    async def get_stuff(self, force: bool = False) -> StuffShortcutable:
        from taho.database.utils import get_stuff # avoid circular import

        return await get_stuff(self, force=force)
    
    async def get_stuff_amount(self, force: bool = False) -> Union[float, int]:
        from taho.database.utils import get_stuff_amount # avoid circular import

        return await get_stuff_amount(self, force=force)

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

class CraftAccessRule(BaseModel):
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
        table = "craft_access"
    
    id = fields.IntField(pk=True)

    craft = fields.ForeignKeyField("main.Craft", related_name="accesses")
    have_access = fields.BooleanField()
    stuff_shortcut = fields.ForeignKeyField("main.AccessRuleShortcut")