from __future__ import annotations
from typing import Any, List, Optional
from tortoise.models import Model
from tortoise import fields
from .role import GuildRole, Role
from .user import User
from .bank import Bank
from .item import Item
import discord
from typing import TYPE_CHECKING
from taho.exceptions import RoleException

if TYPE_CHECKING:
    from discord.ext.commands import AutoShardedBot
    from typing import Dict
    from .role import RoleType

__all__ = (
    "GuildCluster",
    "Guild",
    "ClusterInfo",
    "GuildInfo",
)

class GuildCluster(Model):
    class Meta:
        table = "guild_clusters"
    
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=255)

    infos: fields.ReverseRelation["ClusterInfo"]
    guilds: fields.ReverseRelation["Guild"]
    users: fields.ReverseRelation["User"]
    banks: fields.ReverseRelation["Bank"]
    items: fields.ReverseRelation["Item"]
    roles: fields.ReverseRelation["Role"]

    async def get_info(self, key: str) -> Any:
        async for info in self.infos:
            if info.key == key:
                return info.value
        return None

    def __str__(self):
        return self.name

    async def get_discord_members(self, bot: AutoShardedBot, user_id: int) -> List[discord.Member]:
        """
        Returns a list of discord.Member objects for all the members of the guild.
        """
        members = []
        async for guild in self.guilds:
            members.append(await guild.get_member(bot, user_id))
        return [m for m in members if m]

    async def get_roles(self, bot: AutoShardedBot) -> Dict[Role, List[discord.Role]]:
        """
        Returns a dictionary of roles and their guilds.
        """
        return {role:await role.get_discord_roles(bot) async for role in self.roles}
        
    async def get_common_discord_roles(self, bot: AutoShardedBot) -> Dict[str, List[discord.Role]]:
        """
        Get all the roles that are common to all the guilds in the cluster.
        A role is common if it is named the same way in all the guilds.
        """
        # Fetch all guilds from the cluster
        guilds = await self.guilds.all()
        # Pick one guild to get the roles from
        # All roles will be compared to the ones on the guild
        guild: Guild = guilds.first()
        # For each role in the guild, check if it is common to all the guilds
        # We use the get_common_discord_role function to check if the role is common
        roles = {
            role.name: await self.get_common_discord_role(bot, role, guilds) 
            for role in (await guild.discord_guild(bot)).roles
        }
        # Remove empty lists corresponding to roles that are not common to all the guilds
        return {k: v for k, v in roles.items() if v is not None}

    async def get_commun_discord_role(self, bot: AutoShardedBot, role: discord.Role, guilds: List[Guild]=None) -> List[discord.Role]:
        """
        Returns a list of discord.Role objects that are common to all the guilds in the cluster.
        A role is common if it is named the same way in all the guilds.

        The difference between this method and get_common_discord_roles is that this method
        returns the roles in common with the one given as parameter, whereas get_common_discord_roles
        returns all the roles that are common to all the guilds in the cluster.
        """
        if guilds is None:
            guilds = await self.guilds.all()
        if len(guilds) == 1:
            return [role]
        else:
            roles = []
            guild_roles = [
                (await guild.discord_guild(bot)).roles for guild in guilds
            ]
            for guild_role in guild_roles:
                r = discord.utils.find(lambda r: r.name == role.name, guild_role)
                if not r:
                    return None
                roles.append(r)
            return roles

    async def get_discord_guilds(self, bot: AutoShardedBot) -> List[discord.Guild]:
        """
        Returns a list of discord.Guild objects for all the guilds in the cluster.
        """
        return [await (await guild).discord_guild(bot) async for guild in self.guilds]

    async def create_role(self, bot: AutoShardedBot, role: discord.Role, type: RoleType) -> Role:
        """
        Configure a RP role on a cluster.
        Raises exception if:
        - RoleException: The role already exists;
        - RoleException: The role is not common to all guilds of the cluster.
        """
        roles = []
        for r in (await self.get_roles(bot)).values():
            roles.extend(r)
        if role in roles:
            raise RoleException("Role already exists.")
        common_roles = await self.get_commun_discord_role(bot, role)
        if not common_roles:
            raise RoleException("Role is not common to all guilds of the cluster.")
        # Create the Role instance
        role_obj = await Role.create(cluster=self, type=type)
        from taho.utils.database import get_db_guild # Avoid circular import
        # For each guild of the cluster, create the GuildRole instance
        print()
        objects = [
            GuildRole(role=role_obj, guild=await get_db_guild(r.guild), discord_role_id=r.id)
            for r in common_roles
        ]
        print(objects)
        # Save the Role and GuildRole instances
        await GuildRole.bulk_create(objects=objects)
        return role_obj

class Guild(Model):
    class Meta:
        table = "guilds"

    id = fields.BigIntField(pk=True)
    cluster = fields.ForeignKeyField("main.GuildCluster", related_name="guilds")

    infos: fields.ReverseRelation["GuildInfo"]

    async def get_info(self, key: str) -> Any:
        async for info in self.infos:
            if info.key == key:
                return info.value
        return await self.cluster.get_info(key)

    async def discord_guild(self, bot: AutoShardedBot) -> discord.Guild:
        """
        Get the discord.Guild object for this guild.
        """
        guild = bot.get_guild(self.id)
        if guild and not guild.chunked:
            await guild.chunk()
        return guild
    
    async def get_member(self, bot: AutoShardedBot, user_id: int) -> Optional[discord.Member]:
        """
        Returns a discord.Member object for the user.
        """
        return (await self.discord_guild(bot)).get_member(user_id)
    
    async def get_role(self, bot: AutoShardedBot, role_id: int) -> Optional[discord.Role]:
        """
        Returns a discord.Role object for the role.
        """
        return (await self.discord_guild(bot)).get_role(role_id)

class ClusterInfo(Model):
    class Meta:
        table = "cluster_infos"
    
    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.GuildCluster", related_name="infos")
    key = fields.CharField(max_length=255)
    type = fields.CharField(max_length=255)
    value = fields.CharField(max_length=255)

    def __str__(self):
        return f"{self.key} : {self.value} ({self.type})"
    
    @property
    def py_value(self) -> Any:
        """
        Get the value in Python format.
        """
        if self.type == "int":
            return int(self.value)
        elif self.type == "float":
            return float(self.value)
        elif self.type == "bool":
            return bool(self.value)
        elif self.type == "list":
            return list(self.value)
        else:
            return self.value

class GuildInfo(Model):
    class Meta:
        table = "guild_infos"

    id = fields.IntField(pk=True)

    guild = fields.ForeignKeyField("main.Guild", related_name="infos")
    key = fields.CharField(max_length=255)
    type = fields.CharField(max_length=255)
    value = fields.CharField(max_length=255)

    def __str__(self):
        return f"{self.key} : {self.value} ({self.type})"
    
    @property
    def py_value(self) -> Any:
        """
        Get the value in Python format.
        """
        if self.type == "int":
            return int(self.value)
        elif self.type == "float":
            return float(self.value)
        elif self.type == "bool":
            return bool(self.value)
        elif self.type == "list":
            return list(self.value)
        else:
            return self.value