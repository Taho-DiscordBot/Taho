from __future__ import annotations
from typing import TYPE_CHECKING, Any, List
from tortoise.models import Model
from tortoise import fields
from .item import ItemType, ItemReason
from taho.exceptions import QuantityException, NPCException
from enum import IntEnum
from .npc import NPC

if TYPE_CHECKING:
    from .bank import Bank, BankAccount
    from .role import Role
    from .inventory import Inventory
    from .item import Item, ItemStat, ItemRole
    from .stat import Stat
    from .npc import NPCOwner
    from .server import ServerCluster
    from discord.ext.commands import AutoShardedBot
    import discord



__all__ = (
    "User",
)

class UseType(IntEnum):
    USE = 1
    EQUIP = 2
    UNEQUIP = 3
    GIVE = 4
    DEFAULT = 4


class User(Model):
    """
    Represents a user in the database.
    The user have to be linked to a Cluster.
    The user with the user_id 0 is the default user for a cluster;
    it can be used to store data that is not linked to a specific user
    (ex: the default bank account is linked to the user with user_id 0).
    """
    class Meta:
        table = "users"
    # Defining `id` field is optional, it will be defined automatically
    # if you haven't done it yourself
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField()
    cluster: ServerCluster = fields.ForeignKeyField("main.ServerCluster", related_name="users")

    banks: fields.ReverseRelation["Bank"] # The banks owned by the user
    accounts: fields.ReverseRelation["BankAccount"] # The accounts owned by the user
    inventories: fields.ReverseRelation["Inventory"] # The items in the user's inventory
    npcs: fields.ReverseRelation["NPCOwner"] # The npcs owned by the user

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        print("user initied")
        self._is_npc = None

    async def is_npc(self) -> bool:
        """
        Check if the user is an NPC.
        """
        print("is_npc?")
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

    async def get_discord_member(self, bot: AutoShardedBot) -> List[discord.Member]:
        """
        Get all Member instances of the user from the guilds of the cluster.
        Raises an exception if:
        - NPCException: the user is an NPC
        """
        if await self.is_npc():
            raise NPCException("The user is an NPC")
        return await self.cluster.get_discord_members(bot, self.user_id)

    async def get_roles(self, bot: AutoShardedBot) -> List[Role]:
        """
        Get the roles of the user.
        """
        if await self.is_npc():
            return await (await self.get_npc()).roles.all() # Get the roles of the NPC
        user_roles = []
        cluster_roles = await self.cluster.get_roles(bot)
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
        - the item's type is not "EQUIPEMENT"
        """
        if hotbar.type != ItemType.EQUIPMENT: # Check if the item is an equipement
            return False
        async for inventory in self.inventories:
            if inventory.hotbar == slot: # Check if the slot is already occupied
                inventory.hotbar = None
                await inventory.save()
                await self.item_after_use(inventory, use_type=UseType.UNEQUIP)
        if hotbar.amount > 1: # Check if the item is stacked
            # If the item is stacked, we need to create a new item
            # We split the two items :
            # One with an amount of 1, the item in hotbar
            # The other with the amount of the item's amount - 1
            await hotbar.clone(amount=hotbar.amount-1)
            hotbar.amount = 1
        hotbar.hotbar = slot # Set the hotbar slot and save the item
        await hotbar.save()
        await self.item_after_use(hotbar, use_type=UseType.EQUIP)
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
        if inventory.item.type in (ItemType.EQUIPEMENT, ItemType.CONSUMABLE):
            await self.item_after_use(inventory, amount, use_type)

    async def item_after_use(self, inventory: Inventory, amount: int=1, use_type: int=None) -> None:
        """
        Do something after using an item.
        This method is called after the item is used.
        It calculates the stats/roles to give to the user.

        """
        item: Item = inventory.item
        if use_type == UseType.USE:
            stats: List[ItemStat] = item.stats
            for stat in stats:
                if stat.type == ItemReason.ITEM_USED:
                    await self.add_stat(stat.stat, stat.amount * amount, stat.is_regen)
            roles: List[ItemRole] = item.roles
            for role in roles:
                if role.type == ItemReason.ITEM_USED:
                    await self.add_role(role.role)
        elif use_type == UseType.EQUIP:
            pass
            #stats: List[ItemStat] = item.stats
            #for stat in stats:
            #    if stat.type == ItemReason.ITEM_EQUIPPED:
            #        await self.add_stat(stat.stat, stat.amount * amount, stat.is_regen)
            #roles: List[ItemRole] = item.roles
            #for role in roles:
            #    if role.type == ItemReason.ITEM_EQUIPPED:
            #        await self.add_role(role.role)
        elif use_type == UseType.UNEQUIP:
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

    async def add_role(self, bot: AutoShardedBot, role: Role) -> None:
        """
        Add a role to the user.
        """
        if role in await self.get_roles(bot): # Check if the role is already in the user's roles
            return
        if await self.is_npc():
            await self.get_npc().add_role(role) # Add the role to the NPC
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

    async def remove_role(self, bot: AutoShardedBot, role: Role) -> None:
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


class UserStat(Model):
    class Meta:
        table = "user_stats"

    id = fields.IntField(pk=True)

    user = fields.ForeignKeyField("main.User", related_name="stats")
    stat = fields.ForeignKeyField("main.Stat", related_name="user_stats")
    amount = fields.IntField()
    is_regen = fields.BooleanField()
    maximum = fields.IntField()