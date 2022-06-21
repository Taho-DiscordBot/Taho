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
from tortoise.models import Model
from tortoise import fields
from ..utils import convert_to_type, get_type

if TYPE_CHECKING:
    from discord.ext.commands import AutoShardedBot
    from typing import Any, Optional, Union
    from discord import Member, Role as DRole, Guild


__all__ = (
    "Server",
    "ServerInfo",
)






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

    async def get_guild(self, bot: AutoShardedBot) -> Guild:
        """
        Get the discord.Guild object for this server.
        """
        guild = bot.get_guild(self.id)
        if guild and not guild.chunked:
            await guild.chunk()
        return guild
    
    async def get_member(self, bot: AutoShardedBot, user_id: int) -> Optional[Member]:
        """
        Returns a discord.Member object for the user.
        """
        return (await self.get_guild(bot)).get_member(user_id)
    
    async def get_role(self, bot: AutoShardedBot, role_id: int) -> Optional[DRole]:
        """
        Returns a discord.Role object for the role.
        """
        return (await self.get_guild(bot)).get_role(role_id)

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