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
from tortoise.models import Model
from tortoise import fields
from taho.enums import ItemType, ItemReason

if TYPE_CHECKING:
    from typing import Any, Iterable, Optional
    from tortoise import BaseDBAsyncClient

__all__ = (
    "Item",
    "ItemStat",
    "ItemRole",
)

class Item(Model):
    """Represents an item.

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
        
        .. collapse:: ammo_id

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`null` True

            Python: Optional[:class:`int`]
        
        .. collapse:: charger_size

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
    ammo_id: Optional[:class:`int`]
        The item's ammo ID.
    charger_size: Optional[:class:`int`]
        The item's charger size.
    stats: List[:class:`~taho.database.models.ItemStat`]
        |coro_attr|

        The item's stats.
    roles: List[:class:`~taho.database.models.Role`]
        |coro_attr|

        The item's roles.
    
    """
    class Meta:
        table = 'items'

    id = fields.IntField(pk=True)
    
    cluster = fields.ForeignKeyField('main.Cluster', related_name='items')
    name = fields.CharField(max_length=255)
    emoji = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)
    type = fields.IntEnumField(ItemType, default=ItemType.resource)
    durability: Optional[int] = fields.IntField(null=True)
    cooldown = fields.IntField(null=True) #TODO typing in fields
    ammo_id = fields.IntField(null=True)
    charger_size = fields.IntField(null=True)

    stats: fields.ReverseRelation["ItemStat"]
    roles: fields.ReverseRelation["ItemRole"]

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)
    
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
    
    def __repr__(self) -> str:
        return super().__repr__()
    
    def __hash__(self) -> int:
        return hash(self.__repr__())
    
    def __str__(self) -> str:
        return self.name


    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ammo = None
    
    @property
    def dura(self) -> Optional[int]:
        """
        Optional[:class:`int`]: Shortcut for :attr:`.durability`.
        """
        return self.durability
    
    async def get_ammo(self) -> Optional[Item]:
        """|coro|

        Returns the item's ammo.

        Returns
        -------
        Optional[:class:`~taho.database.models.Item`]
            The item's ammo if it has one.        
        """
        if not self.ammo_id:
            return None
        return await Item.get(id=self.ammo_id)
    
    async def save(
        self,
        using_db: Optional[BaseDBAsyncClient] = None,
        update_fields: Optional[Iterable[str]] = None,
        force_create: bool = False,
        force_update: bool = False,
    ) -> None:
        if self.type == ItemType.resource:
            self.ammo_id = None
            self._ammo = None
            self.charger_size = None
            self.durability = None
            self.cooldown = None
        elif self.type == ItemType.consumable:
            self.ammo_id = None
            self._ammo = None
            self.charger_size = None
            self.cooldown = None
        await super().save(
            using_db=using_db, 
            update_fields=update_fields, 
            force_create=force_create, 
            force_update=force_update
            )

class ItemStat(Model):
    """Represents an item stat.

    .. container:: operations

        .. describe:: x == y

            Checks if two item stats are equal.

        .. describe:: x != y

            Checks if two item stats are not equal.
        
        .. describe:: hash(x)

            Returns the item stat's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: item

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Item`
                - :attr:`related_name` ``stats``
            
            Python: :class:`~taho.database.models.Item`
        
        .. collapse:: stat

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Stat`
                - :attr:`related_name` ``stats``
            
            Python: :class:`~taho.database.models.Stat`
        
        .. collapse:: amount

            Tortoise: :class:`tortoise.fields.IntField`

            Python: :class:`int`
        
        .. collapse:: type

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.ItemReason`
                - :attr:`default` :attr:`taho.enums.ItemReason.item_in_inventory`
            
            Python: :class:`~taho.enums.ItemReason`
        
        .. collapse:: is_regen

            Tortoise: :class:`tortoise.fields.BooleanField`        

                - :attr:`default` True

            Python: :class:`bool`
    
    Attributes
    -----------
    id: :class:`int`
        The item stat's ID.
    item: :class:`~taho.database.models.Item`
        |coro_attr|

        The item stat's item.
    stat: :class:`~taho.database.models.Stat`
        |coro_attr|

        The item stat's stat.
    amount: :class:`int`
        The item stat's amount.
    type: :class:`~taho.enums.ItemReason`
        The item stat's type.
    is_regen: :class:`bool`
        Whether the item stat is a regeneration stat.
    """
    class Meta:
        table = 'item_stats'
    
    id = fields.IntField(pk=True)

    item = fields.ForeignKeyField('main.Item', related_name='stats')
    stat =  fields.ForeignKeyField('main.Stat', related_name='stats')
    amount = fields.IntField()
    type = fields.IntEnumField(ItemReason, default=ItemReason.item_in_inventory)
    is_regen = fields.BooleanField(default=True)

class ItemRole(Model):
    """Represents an item role.

    .. container:: operations

        .. describe:: x == y

            Checks if two item roles are equal.

        .. describe:: x != y

            Checks if two item roles are not equal.
        
        .. describe:: hash(x)

            Returns the item role's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: item

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Item`
                - :attr:`related_name` ``roles``
            
            Python: :class:`~taho.database.models.Item`
        
        .. collapse:: role

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Role`
                - :attr:`related_name` ``roles``
            
            Python: :class:`~taho.database.models.Role`
        
        .. collapse:: type

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.ItemReason`
                - :attr:`default` :attr:`taho.enums.ItemReason.item_in_inventory`
            
            Python: :class:`~taho.enums.ItemReason`
        
    Attributes
    -----------
    id: :class:`int`
        The item role's ID.
    item: :class:`~taho.database.models.Item`
        |coro_attr|

        The item role's item.
    role: :class:`~taho.database.models.Role`
        |coro_attr|

        The item role's role.
    type: :class:`~taho.enums.ItemReason`
        The item role's type.
    """
    class Meta:
        table = 'item_roles'

    id = fields.IntField(pk=True)

    item = fields.ForeignKeyField('main.Item', related_name='roles')
    role = fields.ForeignKeyField('main.Role', related_name='roles')
    amount = fields.IntField()
    type = fields.IntEnumField(ItemReason, default=ItemReason.item_in_inventory)
    