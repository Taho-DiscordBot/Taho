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
from tortoise.exceptions import ValidationError
from taho.enums import ItemType, RewardType
from taho.abc import StuffShortcutable
from .reward import RewardPack, Reward

if TYPE_CHECKING:
    from typing import Any, Iterable, Optional, Dict, List
    from tortoise import BaseDBAsyncClient

__all__ = (
    "Item",
    "ItemRewardPack",
    "ItemReward",
    "ItemAccess",
)

class Item(BaseModel, StuffShortcutable):
    """|shortcutable|
    
    Represents an item.

    .. container:: operations

        .. describe:: x == y

            Checks if two items are equal.

        .. describe:: x != y

            Checks if two items are not equal.
        
        .. describe:: hash(x)

            Returns the item's hash.
        
        .. describe:: str(x)

            Returns the item's name.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: cluster

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Cluster`
                - :attr:`related_name` ``items``
            
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
        
        .. collapse:: description

            Tortoise: :class:`tortoise.fields.TextField`

                - :attr:`null` True
            
            Python: Optional[:class:`str`]
        
        .. collapse:: type

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.ItemType`
                - :attr:`default` :attr:`taho.enums.ItemType.resource`
            
            Python: :class:`~taho.enums.ItemType`

        .. collapse:: durability

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`null` True
            
            Python: Optional[:class:`int`]
        
        .. collapse:: cooldown

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`null` True
            
            Python: Optional[:class:`int`]
        
    Attributes
    -----------
    id: :class:`int`
        The item's ID.
    cluster: :class:`~taho.database.models.Cluster`
        The item's cluster.
    name: :class:`str`
        The item's name.
    emoji: Optional[:class:`str`]
        The item's emoji.
    description: Optional[:class:`str`]
        The item's description.
    type: :class:`~taho.enums.ItemType`
        The item's type.
    durability: Optional[:class:`int`]
        The item's durability.
    cooldown: Optional[:class:`int`]
        The item's cooldown.
    stats: List[:class:`~taho.database.models.ItemStat`]
        |coro_attr|

        The item's stats.
    roles: List[:class:`~taho.database.models.Role`]
        |coro_attr|

        The item's roles.
    
    """
    class Meta:
        table = "items"
        unique_together = (("cluster", "name"),)

    id = fields.IntField(pk=True)
    
    cluster = fields.ForeignKeyField('main.Cluster', related_name='items')
    name = fields.CharField(max_length=255)
    emoji = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)
    type = fields.IntEnumField(ItemType, default=ItemType.resource)

    durability: Optional[int] = fields.IntField(null=True)
    cooldown = fields.IntField(null=True) #TODO typing in fields

    currency = fields.ForeignKeyField('main.Currency', null=True)

    accesses: fields.ReverseRelation["ItemAccess"]
    reward_packs: fields.ReverseRelation["ItemRewardPack"]
    
    def __str__(self) -> str:
        return self.name

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
    
    @property
    def dura(self) -> Optional[int]:
        """
        Optional[:class:`int`]: Shortcut for :attr:`.durability`.
        """
        return self.durability
    
    @property
    def is_currency(self) -> bool:
        """
        :class:`bool`: Whether the item is a currency item.
        """
        return self.type == ItemType.currency
    
    async def get_rewards(self) -> Dict[RewardType, Dict[float, List[ItemReward]]]:
        """
        |coro|
        
        Returns the item's rewards.
        
        Returns
        -------
        :class:`dict`
            The item's rewards.
        

        .. note::

            The returned dictionary is of the form::

                {
                    RewardType.x: {
                        probability: [
                            ItemReward(),
                            ...
                        ],
                    },
                    ...
                }
        
        """
        from taho.utils import RandomHash

        rewards = {x: {} for x in RewardType}
        async for _rewards in self.reward_packs.all().prefetch_related('rewards'):

            reward_list = await _rewards.rewards.all().prefetch_related("stuff_shortcut")
            rewards[_rewards.type][RandomHash(_rewards.luck)] = reward_list
        
        return rewards
    
    @classmethod
    async def from_json(cls, data: Dict[str, Any]) -> Item:
        """
        |coro|
        
        Creates an item from a JSON dictionary.
        
        Parameters
        ----------
        data: :class:`dict`
            The JSON dictionary.
        
        Returns
        -------
        :class:`Item`
            The item.
        
        """
        from taho.database.models import Cluster, Currency, ItemStat, Role

    async def get_display(self) -> str:
        """
        |coro|
        
        Returns the item's display.
        
        Returns
        -------
        :class:`str`
            The item's display.
        """           
        return f"{self.emoji} {self.name}" if self.emoji else self.name


        # cluster = await Cluster.get_or_none(id=data['cluster'])
        # currency = await Currency.get_or_none(id=data['currency']) if 'currency' in data else None
        # stats = [await ItemStat.from_json(x) for x in data['stats']] if 'stats' in data else []
        # roles = [await Role.from_json(x) for x in data['roles']] if 'roles' in data else []

        # return cls(
        #     id=data['id'],
        #     cluster=cluster,
        #     name=data['name'],
        #     emoji=data['emoji'],
        #     description=data['description'],
        #     type=ItemType(data['type']),
        #     durability=data['durability'],
        #     cooldown=data['cooldown'],
        #     currency=currency,
        #     stats=stats,
        #     roles=roles,
        # )

    async def save(
        self,
        using_db: Optional[BaseDBAsyncClient] = None,
        update_fields: Optional[Iterable[str]] = None,
        force_create: bool = False,
        force_update: bool = False,
    ) -> None:
        if self.type == ItemType.resource:
            self.durability = None
            self.cooldown = None
        await super().save(
            using_db=using_db, 
            update_fields=update_fields, 
            force_create=force_create, 
            force_update=force_update
            )


def validate_item_reward_type(value:RewardType):
    if value not in (
        RewardType.passive,
        RewardType.active,
        RewardType.equip,
    ):
        raise ValidationError("Invalid reward type")

class ItemRewardPack(RewardPack):
    """
    Represents a reward pack for an item.

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
        
        .. collapse:: item

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Item`
                - :attr:`related_name` ``reward_packs``
            
            Python: :class:`~taho.database.models.Item`
        
        .. collapse:: type

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.RewardType`
            
            Python: :class:`~taho.enums.RewardType`
        
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
    item: :class:`.Item`
        |coro_attr|

        The reward pack's item.
    type: :class:`~taho.enums.RewardType`
        The item reward's type.
    luck: :class:`float`
        The reward pack's luck.
    rewards: List[:class:`.ItemReward`]
        |coro_attr|

        The rewards included in the reward pack.
    """
    class Meta:
        table = "item_reward_packs"
    

    item = fields.ForeignKeyField('main.Item', related_name='reward_packs')

    type = fields.IntEnumField(RewardType, validators=[validate_item_reward_type])

    rewards: fields.ReverseRelation["ItemReward"]

class ItemReward(Reward):
    """
    Represents an item reward.

    .. container:: operations

        .. describe:: x == y

            Checks if two item rewards are equal.

        .. describe:: x != y

            Checks if two item rewards are not equal.
        
        .. describe:: hash(x)

            Returns the item reward's hash.
        
        .. describe:: str(x)

            Returns the item reward's name.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: pack

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.ItemRewardPack`
                - :attr:`related_name` ``rewards``
            
            Python: :class:`~taho.database.models.ItemRewardPack`
        
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
        The item reward's ID.
    pack: :class:`~taho.database.models.ItemRewardPack`
        The item reward's pack.
    stuff_shortcut: :class:`~taho.database.models.StuffShortcut`
        The item reward's shortcut.
    regeneration: :class:`bool`
        If the shortcut points to a :class:`~taho.database.models.Stat`,
        then this is whether the stat should be regenerated.
    durability: :class:`bool`
        If the shortcut points to a :class:`~taho.database.models.Item`,
        then this is whether it should add durability to it.
    amount: :class:`float`
        The amount of the reward.
    """
    class Meta:
        table = "item_rewards"
    
    pack = fields.ForeignKeyField("main.ItemRewardPack", related_name="rewards")

class ItemAccess(BaseModel):
    """Represents an access to a item.

    .. container:: operations

        .. describe:: x == y

            Checks if two item accesses are equal.

        .. describe:: x != y

            Checks if two item accesses are not equal.
        
        .. describe:: hash(x)

            Returns the item access's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
            
        .. collapse:: item

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Item`
                - :attr:`related_name` ``accesses``
            
            Python: :class:`~taho.database.models.Item`
        
        .. collapse:: have_access

            Tortoise: :class:`tortoise.fields.BooleanField`

            Python: :class:`bool`
        
        .. collapse:: access_shortcut

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.AccessShortcut`
            
            Python: :class:`~taho.database.models.StuffShortcut`
        
    Attributes
    -----------
    id: :class:`int`
        The item access's ID.
    item: :class:`~taho.database.models.Item`
        |coro_attr|

        The item linked to this access.
    have_access: :class:`bool`
        Whether the user/role has access to the item.
    access_shortcut: :class:`~taho.database.models.AccessShortcut`
        |coro_attr|
        
        The shortcut to the entity which has access to the item.
    """
    class Meta:
        table = "item_access"
    
    id = fields.IntField(pk=True)

    item = fields.ForeignKeyField("main.Item", related_name="accesses")
    have_access = fields.BooleanField()
    access_shortcut = fields.ForeignKeyField("main.AccessShortcut")
