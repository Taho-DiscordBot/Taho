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
from tortoise import fields
from taho.enums import ItemType
from typing import TYPE_CHECKING
from taho.abc import StuffShortcutable, TradeStuffShortcutable

if TYPE_CHECKING:
    from typing import Iterable, Optional
    from tortoise import BaseDBAsyncClient



__all__ = (
    "Inventory",
    "Hotbar",
)

class Inventory(BaseModel, StuffShortcutable, TradeStuffShortcutable):
    """|shortcutable|
    
    Represents a :class:`~taho.database.models.Item` in a
    :class:`~taho.database.models.User`'s inventory.

    .. container:: operations

        .. describe:: x == y

            Checks if two inventories are equal.

        .. describe:: x != y

            Checks if two inventories are not equal.
        
        .. describe:: hash(x)

            Returns the inventories's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: owner_shortcut

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.OwnerShortcut`
                - :attr:`related_name` ``inventories``
                - :attr:`null` ``True``
            
            Python: Optional[:class:`~taho.database.models.OwnerShortcut`]
        
        .. collapse:: item

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Item`
                - :attr:`related_name` ``inventories``
        
            Python: :class:`~taho.database.models.Item`
        
        .. collapse:: amount

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`default` 0
            
            Python: :class:`int`
        
        .. collapse:: durability

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`null` True
            
            Python: Optional[:class:`int`]
        
        .. collapse:: ammo

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`null` True
            
            Python: Optional[:class:`int`]
        
    Attributes
    -----------
    id: :class:`int`
        The inventory's ID.
    owner_shortcut: Optional[:class:`~taho.database.models.OwnerShortcut`]
        A shortcut to the owner (user, ...) of this.
        Set to ``None`` if the inventory is not owned by a user
        (used for shops sales).
    item: :class:`~taho.database.models.Item`
        |coro_attr|
        
        The :class:`~taho.database.models.Item` in the inventory.
    amount: :class:`int`
        The amount of the item in the inventory.
    durability: Optional[:class:`int`]
        The durability of the item in the inventory.
    ammo: Optional[:class:`int`]
        The ammo of the item in the inventory.
    """
    class Meta:
        table = "inventories"

    id = fields.IntField(pk=True)

    owner_shortcut = fields.ForeignKeyField("main.OwnerShortcut")
    item = fields.ForeignKeyField("main.Item", related_name="inventories")

    amount = fields.IntField(default=0)
    durability = fields.IntField(null=True)
    ammo = fields.IntField(null=True)



    @property
    def dura(self) -> Optional[int]:
        """
        Optional[:class:`int`]: Shortcut for :attr:`.durability`.
        """
        return self.durability

    async def save(
        self,
        using_db: Optional[BaseDBAsyncClient] = None,
        update_fields: Optional[Iterable[str]] = None,
        force_create: bool = False,
        force_update: bool = False,
    ) -> None:
        if self.item.type == ItemType.resource:
            self.ammo = None
            self.durability = None
        elif self.item.type == ItemType.consumable:
            self.durability = self.dura if (self.dura <= self.item.dura) else self.item.dura #TODO better
            self.ammo = None
        await super().save(
        using_db=using_db,
        update_fields=update_fields,
        force_create=force_create,
        force_update=force_update,
        )

class Hotbar(BaseModel):
    """Represents a :class:`~taho.database.models.Item` in a
    :class:`~taho.database.models.User`'s hotbar.

    .. container:: operations

        .. describe:: x == y

            Checks if two hotbars are equal.

        .. describe:: x != y

            Checks if two hotbars are not equal.
        
        .. describe:: hash(x)

            Returns the hotbars's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: user

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.User`
                - :attr:`related_name` ``hotbars``
            
            Python: :class:`~taho.database.models.User`
        
        .. collapse:: item

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Item`
                - :attr:`related_name` ``hotbars``
        
            Python: :class:`~taho.database.models.Item`
        
        .. collapse:: slot

            Tortoise: :class:`tortoise.fields.IntField`
            
            Python: :class:`int`
        
        .. collapse:: durability

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`null` True
            
            Python: Optional[:class:`int`]
        
        .. collapse:: ammo

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`null` True
            
            Python: Optional[:class:`int`]       
    
    Attributes
    -----------
    id: :class:`int`
        The hotbar's ID.
    user: :class:`~taho.database.models.User`
        |coro_attr|

        The :class:`~taho.database.models.User` that owns the hotbar.
    item: :class:`~taho.database.models.Item`
        |coro_attr|

        The :class:`~taho.database.models.Item` in the hotbar.
    slot: :class:`int`
        The slot in the hotbar.
    durability: Optional[:class:`int`]
        The durability of the item in the hotbar.
    ammo: Optional[:class:`int`]
        The ammo of the item in the hotbar.
    """
    class Meta:
        table = "hotbars"

    id = fields.IntField(pk=True)

    user = fields.ForeignKeyField("main.User", related_name="hotbars")
    item = fields.ForeignKeyField("main.Item", related_name="hotbars")

    slot = fields.IntField()
    durability = fields.IntField(null=True)
    ammo = fields.IntField(null=True)



    @property
    def dura(self) -> Optional[int]:
        """
        Optional[:class:`int`]: Shortcut for :attr:`.durability`.
        """
        return self.durability
