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
from taho.exceptions import QuantityException, NPCException
from taho.enums import ItemUse, ItemType, ItemReason, RoleAddedBy
from .npc import NPC
from taho.abc import AccessShortcutable, OwnerShortcutable

if TYPE_CHECKING:
    from typing import Any, List
    from .bank import Bank, BankAccount
    from .role import Role
    from .inventory import Inventory, Hotbar
    from .item import Item, ItemStat, ItemRole
    from .stat import Stat
    from .npc import NPCOwner
    from .server import Cluster
    from taho import Bot
    from discord import Member

__all__ = (
    "User",
    "UserStat",
    "UserPermission",
)

class User(BaseModel, OwnerShortcutable, AccessShortcutable):
    """|shortcutable|
    
    Represents a user of a cluster.

    .. container:: operations

        .. describe:: x == y

            Checks if two users are equal.

        .. describe:: x != y

            Checks if two users are not equal.
        
        .. describe:: hash(x)

            Returns the user's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: user_id

            Tortoise: :class:`tortoise.fields.IntField`

            Python: :class:`int`

        .. collapse:: cluster

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`taho.database.models.Cluster`
                - :attr:`related_name` ``users``

            Python: :class:`taho.database.models.Cluster`

    Attributes
    -----------
    id: :class:`int`
        The user's ID.
    user_id: :class:`int`
        The user's Discord ID.
    cluster: :class:`~taho.database.models.Cluster`
        The cluster the user is in.
    hotbars: List[:class:`~taho.database.models.Hotbar`]
        |coro_attr|

        The items in the user's hotbar.
    npcs: List[:class:`~taho.database.models.NPCOwner`]
        |coro_attr|

        The NPCs owned by the user.
    permissions: :class:`~taho.database.models.UserPermission`
        |coro_attr|

        The permissions of the user.
    roles: List[:class:`~taho.database.models.UserRole`]
        |coro_attr|

        The roles of the user.
    infos: List[:class:`~taho.database.models.UserInfo`]
        |coro_attr|

        The infos of the user (displayed as a list 
        in user's profile).
    

    .. note::

        The user with the :attr:`.user_id` to 0 is the 
        :attr:`.cluster`'s default account.
    """
    class Meta:
        table = "users"
    # Defining `id` field is optional, it will be defined automatically
    # if you haven't done it yourself
    id = fields.IntField(pk=True)
    
    user_id = fields.BigIntField()
    cluster: Cluster = fields.ForeignKeyField("main.Cluster", related_name="users")

    hotbars: fields.ReverseRelation["Hotbar"] # The hotbars of the user
    npcs: fields.ReverseRelation["NPCOwner"] # The npcs owned by the user
    permissions: fields.OneToOneRelation["UserPermission"] # The permissions of the user
    roles: fields.ReverseRelation["UserRole"] # The roles of the user
    infos: fields.ReverseRelation["UserInfo"] # The infos about the user (displayed
    # as a list in user's profile)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    async def is_npc(self) -> bool:
        """
        Check if the user is an NPC.
        """
        if not hasattr(self, "_is_npc") or self._is_npc is None:
            self._is_npc = await NPC.exists(id=self.user_id)
        return self._is_npc

    async def get_npcs(self) -> List[NPCOwner]:
        """
        Get user's npcs as <NPCOwner>.
        Raises an exception if:
        - NPCException: the user is an NPC
        """
        if await self.is_npc():
            raise NPCException("The user is an NPC")
        return await self.npcs.all()

    async def get_npc(self) -> NPC:
        """
        Get the NPC object if the user in an NPC.
        Raises an exception if:
        - NPCException: the user is not an NPC
        """
        if not await self.is_npc():
            raise NPCException("The user is not an NPC")
        return await NPC.get(id=self.user_id)

    async def get_discord_member(self, bot: Bot) -> List[Member]:
        """
        Get all Member instances of the user from the guilds of the cluster.
        Raises an exception if:
        - NPCException: the user is an NPC
        """
        if await self.is_npc():
            raise NPCException("The user is an NPC")
        return await self.cluster.get_discord_members(bot, self.user_id)

    async def get_roles(self, bot: Bot) -> List[Role]:
        """
        Get the roles of the user.
        """
        if await self.is_npc():
            return await (await self.get_npc()).roles.all() # Get the roles of the NPC
        user_roles = []
        cluster_roles = await self.cluster.get_servers_roles(bot)
        member_roles = [m.roles for m in await self.get_discord_member(bot)]
        for role, roles in cluster_roles.items():
            for r in roles:
                if r in member_roles:
                    user_roles.append(role)
                    break
        return user_roles

    async def set_hotbar(self, hotbar: Inventory, slot: int) -> bool:
        """
        Define hotbar slot for an item in the user's inventory.
        Returns True if done, False if one of the following is true:
        - the item's type is not "equipEMENT"
        """
        if hotbar.type != ItemType.equipment: # Check if the item is an equipement
            return False
        async for inventory in self.inventories:
            if inventory.hotbar == slot: # Check if the slot is already occupied
                inventory.hotbar = None
                await inventory.save()
                await self.item_after_use(inventory, use_type=ItemUse.unequip)
        if hotbar.amount > 1: # Check if the item is stacked
            # If the item is stacked, we need to create a new item
            # We split the two items :
            # One with an amount of 1, the item in hotbar
            # The other with the amount of the item's amount - 1
            await hotbar.clone(amount=hotbar.amount-1)
            hotbar.amount = 1
        hotbar.hotbar = slot # Set the hotbar slot and save the item
        await hotbar.save()
        await self.item_after_use(hotbar, use_type=ItemUse.equip)
        return True

    async def give_item(self, item: Inventory, amount: int=1) -> bool:
        """
        Give an item to the user.
        """
        item.amount += amount
        await item.save()
        return True
    
    async def take_item(self, inventory: Inventory, amount: int=1) -> None:
        """
        Take an item from the user.
        Raises an exception if:
        - QuantityException: the item's amount is less than the amount to take
        """
        if inventory.amount < amount:
            raise QuantityException(
                f"{inventory.name}'s amount ({inventory.amount}) is less than {amount}"
                )
        inventory.amount -= amount
        if inventory.amount == 0:
            await inventory.delete()
        else:
            await inventory.save()

    async def use_item(self, inventory: Inventory, amount: int=1, use_type: int=None) -> None:
        """
        Use an item.
        Raises an exception if:
        - QuantityException: the item's amount is less than 1
        """
        try:
            await self.take_item(inventory, amount)
        except QuantityException as e:
            raise e
        if inventory.item.type in (ItemType.equipment, ItemType.consumable):
            await self.item_after_use(inventory, amount, use_type)

    async def item_after_use(self, inventory: Inventory, amount: int=1, use_type: int=None) -> None:
        """
        Do something after using an item.
        This method is called after the item is used.
        It calculates the stats/roles to give to the user.

        """
        item: Item = inventory.item
        if use_type == ItemUse.use:
            stats: List[ItemStat] = item.stats
            for stat in stats:
                if stat.type == ItemReason.item_used:
                    await self.add_stat(stat.stat, stat.amount * amount, stat.is_regen)
            roles: List[ItemRole] = item.roles
            for role in roles:
                if role.type == ItemReason.item_used:
                    await self.add_role(role.role)
        elif use_type == ItemUse.equip:
            pass
            #stats: List[ItemStat] = item.stats
            #for stat in stats:
            #    if stat.type == ItemReason.item_equipped:
            #        await self.add_stat(stat.stat, stat.amount * amount, stat.is_regen)
            #roles: List[ItemRole] = item.roles
            #for role in roles:
            #    if role.type == ItemReason.item_equipped:
            #        await self.add_role(role.role)
        elif use_type == ItemUse.unequip:
            pass

    async def add_stat(self, stat: Stat, amount: int=1, regen: bool=True) -> None:
        """
        Add a stat to the user.
        """
        if amount < 0:
            return await self.remove_stat(stat, -amount)

    async def remove_stat(self, stat: Stat, amount: int=1) -> None:
        """
        Remove a stat from the user.
        """
        pass

    async def add_role(self, bot: Bot, role: Role) -> None:
        """
        Add a role to the user.
        """
        if role in await self.get_roles(bot): # Check if the role is already in the user's roles
            return
        if await self.is_npc():
            npc = await self.get_npc()
            await npc.add_role(role) # Add the role to the NPC
        else:
            discord_roles = await role.get_discord_roles(bot) # Get the discord roles to add
            # Get the discord members of the user, ordered by guild
            members = {m.guild.id: m for m in await self.get_discord_member(bot)}
            for r in discord_roles:
                try:
                    # Add the role to the member of each guild
                    await members.get(r.guild.id).add_roles(r)
                except:
                    pass

    async def remove_role(self, bot: Bot, role: Role) -> None:
        """
        Remove a role from the user.
        """
        if not role in await self.get_roles(bot): # Check if the user already has the role
            return
        if await self.is_npc():
            await self.get_npc().remove_role(role) # Remove the role from the NPC
        else:
            discord_roles = await role.get_discord_roles(bot) # Get the discord roles to remove
            # Get the discord members of the user, ordered by guild
            members = {m.guild.id: m for m in await self.get_discord_member(bot)}
            for r in discord_roles:
                try:
                    # Remove the role from the member of each guild
                    await members.get(r.guild.id).remove_roles(r)
                except:
                    pass

class UserStat(BaseModel):
    """Represents a stat a user have.

    .. container:: operations

        .. describe:: x == y

            Checks if two stats are equal.

        .. describe:: x != y

            Checks if two stats are not equal.
        
        .. describe:: hash(x)

            Returns the stat's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: user

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.User`
                - :attr:`related_name` ``stats``
            
            Python: :class:`~taho.database.models.User`
        
        .. collapse:: stat

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Stat`
                - :attr:`related_name` ``user_stats``

            Python: :class:`~taho.database.models.Stat`
        
        .. collapse:: amount

            Tortoise: :class:`tortoise.fields.IntField`

            Python: :class:`int`

        .. collapse:: is_regen

            Tortoise: :class:`tortoise.fields.BooleanField`

                - :attr:`null` ``True``

            Python: Optional[:class:`bool`]

    Attributes
    -----------
    id: :class:`int`
        The stat's ID.
    user: :class:`~taho.database.models.User`
        The user who have the stat.
    stat: :class:`~taho.database.models.Stat`
        The stat.
    amount: :class:`int`
        The amount of the stat.
    is_regen: Optional[:class:`bool`]
        Whether the stat is regenerable.
    """
    class Meta:
        table = "user_stats"

    id = fields.IntField(pk=True)

    user = fields.ForeignKeyField("main.User", related_name="stats")
    stat = fields.ForeignKeyField("main.Stat", related_name="user_stats")
    amount = fields.IntField()
    is_regen = fields.BooleanField(null=True)
    maximum = fields.IntField() #todo penser à ça

class UserPermission(BaseModel):
    """Represents a RP Permission of a :class:`~taho.database.models.User`.
    
    .. container:: operations
    
        .. describe:: x == y

            Checks if two permissions are equal.
        
        .. describe:: x != y
        
            Checks if two permissions are not equal.
        
        .. describe:: hash(x)

            Returns the permission's hash.
        
    .. container:: fields

        .. collapse:: user

            Tortoise: :class:`tortoise.fields.OneToOneField`

                - :attr:`pk` ``True``
                - :attr:`related_model` :class:`~taho.database.models.User`
                - :attr:`related_name` ``'permission'``
            
            Python: :class:`int`
        
        .. collapse:: permission

            Tortoise: :class:`tortoise.fields.BigIntField`

                - :attr:`default` ``0``
        
            Python: :class:`int`
    
    Attributes
    -----------
    user: :class:`~taho.database.models.User`
        The user on which the permission is set.
    permissions: :class:`int`
        The int representation of the permission.
    """
    class Meta:
        table = "user_permissions"

    user = fields.OneToOneField("main.User", pk=True, related_name="permission")
    permission = fields.BigIntField(default=0)

class UserRole(BaseModel):
    """Represents a role of a :class:`~taho.database.models.User`.
    
    .. container:: operations
    
        .. describe:: x == y

            Checks if two roles are equal.
        
        .. describe:: x != y
        
            Checks if two roles are not equal.
        
        .. describe:: hash(x)

            Returns the role's hash.
        
    .. container:: fields

        .. collapse:: id

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True
            
            Python: :class:`int`

        .. collapse:: user

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.User`
                - :attr:`related_name` ``roles``
            
            Python: :class:`~taho.database.models.User`
        
        .. collapse:: role

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Role`
            
            Python: :class:`~taho.database.models.Role`

        .. collapse:: added_by

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum_type` :class:`~taho.enums.RoleAddedBy`
            
            Python: :class:`~taho.enums.RoleAddedBy`

    Attributes
    -----------
    id: :class:`int`
        The role's ID.
    user: :class:`~taho.database.models.User`
        The user on which the role is set.
    role: :class:`~taho.database.models.Role`
        The role.
    added_by: :class:`~taho.enums.RoleAddedBy`
        The way the role was added.
    """
    class Meta:
        table = "user_roles"

    id = fields.IntField(pk=True)

    user = fields.ForeignKeyField("main.User", related_name="roles")
    role = fields.ForeignKeyField("main.Role")
    added_by = fields.IntEnumField(RoleAddedBy)


class UserInfo(BaseModel):
    """Represents a user's info.
    
    .. container:: operations
    
        .. describe:: x == y

            Checks if two infos are equal.
        
        .. describe:: x != y
        
            Checks if two infos are not equal.
        
        .. describe:: hash(x)

            Returns the info's hash.
        
    .. container:: fields

        .. collapse:: id

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True
            
            Python: :class:`int`

        .. collapse:: user

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.User`
                - :attr:`related_name` ``infos``
            
            Python: :class:`~taho.database.models.User`
        
        .. collapse:: value

            Tortoise: :class:`tortoise.fields.TextField`

            Python: :class:`str`

    Attributes
    -----------
    id: :class:`int`
        The info's ID.
    user: :class:`~taho.database.models.User`
        The user on which the info is set.
    value: :class:`str`
        The value of the info.
    """
    class Meta:
        table = "user_infos"

    id = fields.IntField(pk=True)

    user = fields.ForeignKeyField("main.User", related_name="infos")
    value = fields.TextField()