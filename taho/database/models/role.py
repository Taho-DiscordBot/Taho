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
from ..enums import RoleType
from tortoise.models import Model
from tortoise import fields
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord.ext.commands import AutoShardedBot
    from discord import Role as DRole
    from typing import List

__all__ = (
    "Role",
)
class Role(Model):
    class Meta:
        table = "roles"

    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.ServerCluster", related_name="roles")
    type = fields.IntEnumField(RoleType, default=RoleType.DEFAULT)

    server_roles: fields.ReverseRelation["ServerRole"]

    async def get_discord_roles(self, bot: AutoShardedBot) -> List[DRole]:
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

    async def discord_role(self, bot: AutoShardedBot) -> DRole:
        """
        Get the discord.Role object for this role in the guild.
        """
        server = await self.server
        guild = await server.get_guild(bot)
        return guild.get_role(self.d_role_id)