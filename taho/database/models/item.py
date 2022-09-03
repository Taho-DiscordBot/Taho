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
import asyncio
from tortoise import fields
from tortoise.exceptions import ValidationError
from taho.enums import ItemType, RewardType
from taho.abc import StuffShortcutable
from .reward import RewardPack, Reward
from .access_rule import AccessRule

if TYPE_CHECKING:
    from typing import Any, Iterable, Optional, Dict, List
    from tortoise import BaseDBAsyncClient

__all__ = (
    "Item",
    "ItemRewardPack",
    "ItemReward",
    "ItemAccessRule",
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
        
        ..collapse:: currency

            Tortoise: :class:`tortoise.fields.OneToOneField`

                - :attr:`related_model` :class:`~taho.database.models.Currency`
                - :attr:`related_name` ``item``
                - :attr:`null` ``True``
            
            Python: Optional[:class:`~taho.database.models.Currency`]

        
    Attributes
    -----------
    id: :class:`int`
        The item's ID.
    cluster: :class:`~taho.database.models.Cluster`
        |coro_attr|

        The item's cluster.
    name: :class:`str`
        The item's name.
    emoji: Optional[:class:`~taho.Emoji`]
        The item's emoji.
    description: Optional[:class:`str`]
        The item's description.
    type: :class:`~taho.enums.ItemType`
        The item's type.
    durability: Optional[:class:`int`]
        The item's durability.
    cooldown: Optional[:class:`int`]
        The item's cooldown.
    currency: Optional[:class:`~taho.database.models.Currency`]
        |coro_attr|

        If the item's type is :attr:`~taho.enums.ItemType.currency`, 
        this is the currency linked to the item.
    access_rules: List[:class:`~taho.database.models.ItemAccessRule`]
        |coro_attr|

        The item's access rules.
    rewards: List[:class:`~taho.database.models.ItemReward`]
        |coro_attr|

        The item's rewards.
    
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

    currency = fields.OneToOneField('main.Currency', related_name="item", null=True)

    access_rules: fields.ReverseRelation["ItemAccessRule"]
    reward_packs: fields.ReverseRelation["ItemRewardPack"]
    
    def __str__(self) -> str:
        return self.get_display()

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

    def get_display(self, long: bool = False) -> str:
        """
        Returns the item's display.

        Parameters
        -----------
        long: :class:`bool`
            Whether to return a long display.
        
        Returns
        -------
        :class:`str`
            The item's display.
        """
        from taho.babel import _
        babel_vars = {
        }
        babel_vars["item_display"] = f"{self.emoji} {self.name}" if self.emoji else self.name

        if long: 
            from taho.enums import get_item_type_text

            babel_vars["type"] = get_item_type_text(self.type)
            if self.dura:
                dura_display = _("Infinite") if self.dura == -1 else str(self.dura)
                babel_vars["durability"] = dura_display

            if self.dura:
                display = _(
                    "**%(item_display)s** - %(type)s (durability: *%(durability)s*)",
                    **babel_vars
                )
            else:
                display = _(
                    "**%(item_display)s** - %(type)s",
                    **babel_vars
                )
        else:

            display = _(
                "**%(item_display)s**",
                **babel_vars
            )
        
        return display

    async def to_dict(self, to_edit: bool = False) -> Dict[str, Any]:
        """
        |coro|
        
        Returns the item's dictionary.

        Parameters
        -----------
        to_edit: :class:`bool`
            Whether to return the item's edit dictionary.
            This will remove several keys from the dictionary.
        
        Returns
        -------
        :class:`dict`
            The item's dictionary.
        """

        item_dict = {
            "id": self.id,
            "cluster_id": self.cluster_id,
            "name": self.name,
            "emoji": self.emoji,
            "description": self.description,
            "type": self.type,
            "durability": self.durability,
            "cooldown": self.cooldown,
            "currency_id": self.currency_id,
            "currency": await self.currency if self.currency_id else None,
            "access_rules": [
                await rule.to_abstract() async for rule in self.access_rules.all()
            ],
            "reward_packs": [
                await pack.to_abstract() async for pack in self.reward_packs.all()
            ],
        }

        if to_edit:
            item_dict.pop("cluster_id", None)
            item_dict.pop("currency_id", None)

        return item_dict

    async def edit(self, **options) -> None:
        """|coro|

        Edits the item.

        Parameters
        -----------
        options: :class:`dict`
            The fields to edit.
            The keys are the field names.
        """
        edit_dict = {}
        queries = []
        for option, value in options.items():
            if option == "access_rules":
                queries.append(self.access_rules.all().delete())
                if value:
                    for rule in value:
                        queries.append(rule.to_db_access(
                            ItemAccessRule,
                            self
                        ))
            
            elif option == "reward_packs":
                queries.append(self.reward_packs.all().delete())
                if value:
                    for pack in value:
                        queries.append(pack.to_db_pack(
                            ItemRewardPack,
                            ItemReward,
                            self
                        ))

            else:
                edit_dict[option] = value
        
        self.update_from_dict(edit_dict)

        await self.save()
        await asyncio.gather(*queries)


    async def save(
        self,
        using_db: Optional[BaseDBAsyncClient] = None,
        update_fields: Optional[Iterable[str]] = None,
        force_create: bool = False,
        force_update: bool = False,
    ) -> None:
        if self.type in (ItemType.resource, ItemType.currency):
            self.durability = None
            self.cooldown = None
        
        if self.type != ItemType.currency:
            self.currency = None
            self.currency_id = None
        
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

class ItemAccessRule(AccessRule):
    """Represents an access rule to a item.

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
            
        .. collapse:: item

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Item`
                - :attr:`related_name` ``access_rules``
            
            Python: :class:`~taho.database.models.Item`
        
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
        The item access's ID.
    item: :class:`~taho.database.models.Item`
        |coro_attr|

        The item linked to this access.
    have_access: :class:`bool`
        Whether the user/role has access to the item.
    access_shortcut: :class:`~taho.database.models.AccessRuleShortcut`
        |coro_attr|
        
        The shortcut to the entity which has access to the item.
    """
    class Meta:
        table = "item_access_rules"
    
    id = fields.IntField(pk=True)

    item = fields.ForeignKeyField("main.Item", related_name="access_rules")
