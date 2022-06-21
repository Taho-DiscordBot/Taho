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
from tortoise.models import Model
from tortoise import fields
from ..enums import ItemType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Iterable, Optional
    from tortoise import BaseDBAsyncClient



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

    @property
    def dura(self) -> Optional[int]:
        """
        Shortcut for <Inventory>.durability
        """
        return self.durability

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
            self.durability = self.dura if (self.dura <= self.item.dura) else self.item.dura #TODO better
            self.ammo = None
            self.hotbar = None
        elif self.item.type == ItemType.EQUIPMENT:
            self.ammo = self.ammo if (self.ammo<=self.item.charger_size) else self.item.charger_size #TODO better       
            await super().save(
            using_db=using_db,
            update_fields=update_fields,
            force_create=force_create,
            force_update=force_update,
            )
