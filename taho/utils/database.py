from taho.database.models import Guild
from tortoise.exceptions import DoesNotExist
import discord
from typing import Optional

__all__ = (
    "get_db_guild",
)

async def get_db_guild(guild: discord.Guild) -> Optional[Guild]:
    """
    Return a Guild record of the Database from a discord Guild.
    """
    try:
        return await Guild.get(id=guild.id)
    except DoesNotExist:
        return None