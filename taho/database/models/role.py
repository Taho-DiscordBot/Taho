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

    cluster = fields.ForeignKeyField("main.GuildCluster", related_name="roles")
    type = fields.IntEnumField(RoleType, default=RoleType.DEFAULT)

    guild_roles: fields.ReverseRelation["GuildRole"]

    async def get_discord_roles(self, bot: AutoShardedBot) -> List[discord.Role]:
        """
        Returns a list of discord.Role objects.
        """
        return [
            await (await guild_role.guild).get_role(bot, guild_role.discord_role_id) 
            async for guild_role in self.guild_roles
            ]

class GuildRole(Model):
    class Meta:
        table = "guild_roles"

    id = fields.IntField(pk=True)

    role = fields.ForeignKeyField("main.Role", related_name="guild_roles")
    guild = fields.ForeignKeyField("main.Guild", related_name="guild_roles")
    discord_role_id = fields.BigIntField()

    async def discord_role(self, bot: AutoShardedBot) -> discord.Role:
        """
        Get the discord.Role object for this role in the guild.
        """
        return (await self.guild.discord_guild(bot)).get_role(self.role_id)