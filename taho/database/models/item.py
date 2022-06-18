from typing import Any, Iterable, Optional
from tortoise.models import Model
from tortoise import BaseDBAsyncClient, fields
from enum import IntEnum

__all__ = (
    "ItemType",
    "ItemReason",
    "Item",
    "ItemStat"
)

class ItemType(IntEnum):
    RESOURCE = 0
    CONSUMABLE = 1
    EQUIPMENT = 2

class ItemReason(IntEnum):
    ITEM_USED = 1
    ITEM_EQUIPPED = 2
    ITEM_IN_INVENTORY = 3

class ItemUse(IntEnum):
    USE = 1
    EQUIP = 2
    GIVE = 3


class Item(Model):
    class Meta:
        table = 'items'

    id = fields.IntField(pk=True)
    
    cluster = fields.ForeignKeyField('main.ServerCluster', related_name='items')
    name = fields.CharField(max_length=255)
    emoji = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)
    type = fields.IntEnumField(ItemType, default=ItemType.RESOURCE)
    durability: Optional[int] = fields.IntField(null=True)
    cooldown = fields.IntField(null=True) #TODO typing in fields
    ammo_id = fields.IntField(null=True)
    charger_size = fields.IntField(null=True)

    stats: fields.ReverseRelation["ItemStat"]
    roles: fields.ReverseRelation["ItemRole"]

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ammo = None
    
    @property
    def dura(self) -> Optional[int]:
        """
        Shortcut for <Item>.durability
        """
        return self.durability
    
    async def ammo(self) -> Optional["Item"]:
        if self._ammo:
            return self._ammo
        if self.ammo_id:
            self._ammo = await Item.get(id=self.ammo_id)
            return self._ammo
    
    async def save(
        self,
        using_db: Optional[BaseDBAsyncClient] = None,
        update_fields: Optional[Iterable[str]] = None,
        force_create: bool = False,
        force_update: bool = False,
    ) -> None:
        if self.type == ItemType.RESOURCE:
            self.ammo_id = None
            self._ammo = None
            self.charger_size = None
            self.durability = None
            self.cooldown = None
        elif self.type == ItemType.CONSUMABLE:
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
    class Meta:
        table = 'item_stats'
    
    id = fields.IntField(pk=True)

    item = fields.ForeignKeyField('main.Item', related_name='stats')
    stat =  fields.ForeignKeyField('main.Stat', related_name='stats')
    amount = fields.IntField()
    type = fields.IntEnumField(ItemReason, default=ItemReason.ITEM_IN_INVENTORY)
    is_regen = fields.BooleanField(default=True)

class ItemRole(Model):
    class Meta:
        table = 'item_roles'

    id = fields.IntField(pk=True)

    item = fields.ForeignKeyField('main.Item', related_name='roles')
    role = fields.ForeignKeyField('main.Role', related_name='roles')
    amount = fields.IntField()
    type = fields.IntEnumField(ItemReason, default=ItemReason.ITEM_IN_INVENTORY)
    