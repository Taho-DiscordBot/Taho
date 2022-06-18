from __future__ import annotations
from tortoise.models import Model
from tortoise import fields
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord.ext.commands import AutoShardedBot
    import discord
    from typing import List

__all__ = (
    "RoleType",
    "Role",
)


class RoleType(IntEnum):
    DEFAULT = 0
    JOB = 1
    CLASS = 2
    OTHER = 3

class Role(Model):
    class Meta:
        table = "roles"

    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.ServerCluster", related_name="roles")
    type = fields.IntEnumField(RoleType, default=RoleType.DEFAULT)

    server_roles: fields.ReverseRelation["ServerRole"]

    async def get_discord_roles(self, bot: AutoShardedBot) -> List[discord.Role]:
        """
        Returns a list of discord.Role objects.
        """
        return [
            await (await server_role.server).get_role(bot, server_role.d_role_id) 
            async for server_role in self.server_roles
            ]

class ServerRole(Model):
    class Meta:
        table = "server_roles"

    id = fields.IntField(pk=True)

    role = fields.ForeignKeyField("main.Role", related_name="server_roles")
    server = fields.ForeignKeyField("main.Server", related_name="server_roles")
    discord_role_id = fields.BigIntField()

    @property
    def d_role_id(self) -> int:
        return self.discord_role_id

    async def discord_role(self, bot: AutoShardedBot) -> discord.Role:
        """
        Get the discord.Role object for this role in the guild.
        """
        server = await self.server
        guild = await server.get_guild(bot)
        return guild.get_role(self.d_role_id)