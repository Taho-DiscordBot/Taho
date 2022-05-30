from typing import Iterable, Optional
from tortoise.models import Model
from tortoise import BaseDBAsyncClient, fields
from .item import ItemType

__all__ = (
    "Inventory",
)

class Inventory(Model):
    class Meta:
        table = "inventories"

    id = fields.IntField(pk=True)

    user = fields.ForeignKeyField("main.User", related_name="inventories")
    item = fields.ForeignKeyField("main.Item", related_name="inventories")

    amount = fields.IntField(default=0)
    durability = fields.IntField(null=True)
    ammo = fields.IntField(null=True)
    hotbar = fields.IntField(null=True)

    async def save(
        self,
        using_db: Optional[BaseDBAsyncClient] = None,
        update_fields: Optional[Iterable[str]] = None,
        force_create: bool = False,
        force_update: bool = False,
    ) -> None:
        if self.item.type == ItemType.RESOURCE:
            self.ammo = None
            self.durability = None
            self.hotbar = None
        elif self.item.type == ItemType.CONSUMABLE:
            self.durability = self.durability if self.durability <= self.item.durability else self.item.durability
            self.ammo = None
            self.hotbar = None
        elif self.item.type == ItemType.EQUIPMENT:
            self.ammo = self.ammo if self.ammo <= self.item.charger_size else self.item.charger_size
        await super().save(
            using_db=using_db,
            update_fields=update_fields,
            force_create=force_create,
            force_update=force_update,
        )
