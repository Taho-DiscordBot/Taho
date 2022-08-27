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

if TYPE_CHECKING:
    from taho import Bot
    from typing import Optional
    import discord

__all__ = (
    "get_discord_guild",
    "get_discord_role",
    "get_discord_member"
)

async def get_discord_guild(bot: Bot, guild_id: int) -> Optional[discord.Guild]:
    guild = bot.get_guild(guild_id)
    if guild and not guild.chunked:
        await guild.chunk()
    return guild

async def get_discord_role(bot: Bot, guild_id: int, role_id: int) -> Optional[discord.Role]:
    guild = await get_discord_guild(bot, guild_id)
    if not guild:
        return None
    return guild.get_role(role_id)

async def get_discord_member(bot: Bot, guild_id: int, user_id: int) -> Optional[discord.Member]:
    guild = await get_discord_guild(bot, guild_id)
    if not guild:
        return None
    return guild.get_member(user_id)