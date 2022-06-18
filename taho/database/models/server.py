from __future__ import annotations
from typing import Any, List, Optional, Union
from tortoise.models import Model
from tortoise import fields
from .role import ServerRole, Role
from .user import User
from .bank import Bank
from .item import Item
import discord
from typing import TYPE_CHECKING
from taho.exceptions import RoleException
from enum import IntEnum

if TYPE_CHECKING:
    from discord.ext.commands import AutoShardedBot
    from typing import Dict
    from .role import RoleType

__all__ = (
    "ServerCluster",
    "Server",
    "ClusterInfo",
    "ServerInfo",
)

class InfoType(IntEnum):
    NULL = 0
    BOOL = 1
    INT = 2
    STRING = 3
    FLOAT = 4

def convert_to_type(value: Any, type_: InfoType) -> Any:
    if type_ == InfoType.NULL:
        return None
    converters = {
        InfoType.BOOL: bool,
        InfoType.INT: int,
        InfoType.STRING: str,
        InfoType.FLOAT: float
    }
    return converters[type_](value)

def get_type(value: Any) -> InfoType:
    if value is None:
        return InfoType.NULL
    types = {
        bool: InfoType.BOOL,
        int: InfoType.INT,
        str: InfoType.STRING,
        float: InfoType.FLOAT
    }
    return types[type(value)]

class ServerCluster(Model):
    class Meta:
        table = "server_clusters"
    
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=255)

    infos: fields.ReverseRelation["ClusterInfo"]
    servers: fields.ReverseRelation["Server"]
    users: fields.ReverseRelation["User"]
    banks: fields.ReverseRelation["Bank"]
    items: fields.ReverseRelation["Item"]
    roles: fields.ReverseRelation["Role"]

    async def get_info(self, key: str) -> Optional[Union[str, int, float, None]]:
        """
        Gets the value of a key in the cluster's info.

        Raises KeyError if the key does not exist.
        """
        async for info in self.infos:
            if info.key == key:
                return info.py_value
        raise KeyError(f"No info with key {key}")
    
    async def set_info(self, key: str, value: Optional[Union[str, int, float, None]]) -> None:
        """
        Sets the value of a key in the cluster's info.
        If the value is None, the info is deleted.

        Raises KeyError if the key does not exist (only for deletion).
        """
        if value is None:
            try:
                await self.infos.filter(key=key).delete()
            except:
                raise KeyError(f"No info with key {key}")
        async for info in self.infos:
            if info.key == key:
                info.value = value
                info.type = get_type(value)
                await info.save()
                return
        await ClusterInfo.create(
            cluster=self,
            key=key,
            value=value,
            type=get_type(value)
        )

    def __str__(self):
        return self.name

    async def get_discord_members(self, bot: AutoShardedBot, user_id: int) -> List[discord.Member]:
        """
        Returns a list of discord.Member objects for all the members of the guild.
        """
        members = []
        async for server in self.servers:
            members.append(await server.get_member(bot, user_id))
        return [m for m in members if m]

    async def get_roles(self, bot: AutoShardedBot) -> Dict[Role, List[discord.Role]]:
        """
        Returns a dictionary of roles on all guilds.
        """
        return {role:await role.get_discord_roles(bot) async for role in self.roles}
        
    async def get_common_discord_roles(self, bot: AutoShardedBot) -> Dict[str, List[discord.Role]]:
        """
        Get all the roles that are common to all the guilds in the cluster.
        A role is common if it is named the same way in all the guilds.
        """
        # Fetch all guilds from the cluster
        servers = await self.servers.all()
        # Pick one guild to get the roles from
        # All roles will be compared to the ones on the guild
        server: Server = servers.first()
        # For each role in the guild, check if it is common to all the guilds
        # We use the get_common_discord_role function to check if the role is common
        roles = {
            role.name: await self.get_common_discord_role(bot, role, servers) 
            for role in (await server.get_guild(bot)).roles
        }
        # Remove empty lists corresponding to roles that are not common to all the guilds
        return {k: v for k, v in roles.items() if v is not None}

    async def get_commun_discord_role(self, bot: AutoShardedBot, role: discord.Role, servers: List[Server]=None) -> List[discord.Role]:
        """
        Returns a list of discord.Role objects that are common to all the guilds in the cluster.
        A role is common if it is named the same way in all the guilds.

        The difference between this method and get_common_discord_roles is that this method
        returns the roles in common with the one given as parameter, whereas get_common_discord_roles
        returns all the roles that are common to all the guilds in the cluster.
        """
        if servers is None:
            servers = await self.servers.all()
        if len(servers) == 1:
            return [role]
        else:
            roles = []
            guild_roles = [
                (await server.get_guild(bot)).roles for server in servers
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
        return [await (await server).get_guild(bot) async for server in self.servers]

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
        # For each guild of the cluster, create the ServerRole instance
        objects = [
            ServerRole(role=role_obj, server=await get_db_guild(r.guild), discord_role_id=r.id)
            for r in common_roles
        ]
        # Save the Role and ServerRole instances
        await ServerRole.bulk_create(objects=objects)
        return role_obj

class Server(Model):
    class Meta:
        table = "servers"

    id = fields.BigIntField(pk=True)
    cluster = fields.ForeignKeyField("main.ServerCluster", related_name="servers")

    infos: fields.ReverseRelation["ServerInfo"]

    async def get_info(self, key: str) -> Optional[Union[str, int, float, None]]:
        """
        Gets the value of a key in the cluster's info.

        Raises KeyError if the key does not exist.
        """
        async for info in self.infos:
            if info.key == key:
                return info.py_value
        return await self.cluster.get_info(key)
    
    async def set_info(self, key: str, value: Optional[Union[str, int, float, None]]) -> None:
        """
        Sets the value of a key in the cluster's info.
        If the value is None, the info is deleted.

        Raises KeyError if the key does not exist (only for deletion).
        """
        if value is None:
            try:
                await self.infos.filter(key=key).delete()
            except:
                raise KeyError(f"No info with key {key}")
        async for info in self.infos:
            if info.key == key:
                info.value = value
                info.type = get_type(value)
                await info.save()
                return
        await ServerInfo.create(
            server=self,
            key=key,
            value=value,
            type=get_type(value)
        )

    async def get_guild(self, bot: AutoShardedBot) -> discord.Guild:
        """
        Get the discord.Guild object for this server.
        """
        guild = bot.get_guild(self.id)
        if guild and not guild.chunked:
            await guild.chunk()
        return guild
    
    async def get_member(self, bot: AutoShardedBot, user_id: int) -> Optional[discord.Member]:
        """
        Returns a discord.Member object for the user.
        """
        return (await self.get_guild(bot)).get_member(user_id)
    
    async def get_role(self, bot: AutoShardedBot, role_id: int) -> Optional[discord.Role]:
        """
        Returns a discord.Role object for the role.
        """
        return (await self.get_guild(bot)).get_role(role_id)

class ClusterInfo(Model):
    class Meta:
        table = "cluster_infos"
    
    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.ServerCluster", related_name="infos")
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
        return convert_to_type(self.value, self.type)

class ServerInfo(Model):
    class Meta:
        table = "server_infos"

    id = fields.IntField(pk=True)

    server = fields.ForeignKeyField("main.Server", related_name="infos")
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
        return convert_to_type(self.value, self.type)