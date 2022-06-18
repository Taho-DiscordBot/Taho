from __future__ import annotations
from tortoise import Tortoise
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord.ext.commands import AutoShardedBot
    from sshtunnel import SSHTunnelForwarder


_models = [
    "taho.database.models.user",
    "taho.database.models.cluster",
    "taho.database.models.server",
    "taho.database.models.bank",
    "taho.database.models.item",
    "taho.database.models.inventory",
    "taho.database.models.role",
    "taho.database.models.stat",
    "taho.database.models.job",
    "taho.database.models.npc",
    ]

async def init_db(bot: AutoShardedBot, tunnel: SSHTunnelForwarder, config: dict=None, _create_db: bool=False) -> None:
    if not config:
        config = bot.config
    # If the SSH tunnel is not used, we can use the default port
    # The SSH tunnel creates a new port for the DB
    port = tunnel.local_bind_port if tunnel else config["DB_PORT"]
    await Tortoise.init(
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "database": config["DB_NAME"],
                        "host": config["DB_HOST"],
                        "password": config["DB_PASSWORD"],
                        "port": port,
                        "user": config["DB_USERNAME"],
                        "schema": config["DB_SCHEMA"],
                    },
                }
            },
            "apps": {
                "main": {"models": _models, "default_connection": "default"}
            },
        },
        _create_db=_create_db
    )

    if _create_db:
        await Tortoise.generate_schemas()
    #print(Tortoise)
    #conn = Tortoise.get_connection('default')
    #await conn.execute_script("""
    #DROP TABLE IF EXISTS guild_clusters CASCADE;
    #DROP TABLE IF EXISTS guilds CASCADE;
    #DROP TABLE IF EXISTS users CASCADE;
    #DROP TABLE IF EXISTS banks CASCADE;
    #DROP TABLE IF EXISTS guild_infos CASCADE;
    #DROP TABLE IF EXISTS cluster_infos CASCADE;
    #DROP TABLE IF EXISTS bank_accounts CASCADE;
    #DROP TABLE IF EXISTS bank_operations CASCADE;
    #DROP TABLE IF EXISTS bank_infos CASCADE;
    #DROP TABLE IF EXISTS items CASCADE;
    #DROP TABLE IF EXISTS inventories CASCADE;
    #DROP TABLE IF EXISTS roles CASCADE;
    #DROP TABLE IF EXISTS stats CASCADE;
    #DROP TABLE IF EXISTS item_roles CASCADE;
    #DROP TABLE IF EXISTS item_stats CASCADE;
    #DROP TABLE IF EXISTS jobs CASCADE;
    #DROP TABLE IF EXISTS job_rewards CASCADE;
    #DROP TABLE IF EXISTS npcs CASCADE;
    #DROP TABLE IF EXISTS npc_roles CASCADE;
    #DROP TABLE IF EXISTS npc_owners CASCADE;
    #""")
    return True