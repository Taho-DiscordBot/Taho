from taho.database.models import Server, ServerCluster
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model
import discord
from typing import Optional, List

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
    
async def get_cluster(guild: discord.Guild) -> Optional[ServerCluster]:
    server = await get_db_guild(guild)
    if server:
        return await server.cluster
    return None