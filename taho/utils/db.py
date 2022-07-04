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
from taho.database import Server
from tortoise.exceptions import DoesNotExist
import discord

if TYPE_CHECKING:
    from typing import Optional
    from taho.database import Cluster



__all__ = (
    "get_db_guild",
)

async def get_db_guild(guild: discord.Guild) -> Optional[Server]:
    """
    Return a Server record of the Database from a discord Guild.
    """
    try:
        return await Server.get(id=guild.id)
    except DoesNotExist:
        return None
    
async def get_cluster(guild: discord.Guild) -> Optional[Cluster]:
    server = await get_db_guild(guild)
    if server:
        return await server.cluster
    return None