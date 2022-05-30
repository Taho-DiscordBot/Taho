from __future__ import annotations
from tortoise import Tortoise
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord.ext.commands import AutoShardedBot
    from sshtunnel import SSHTunnelForwarder


_models = [
    "taho.database.models.user",
    "taho.database.models.guild",
    "taho.database.models.bank",
    ]

async def init_db(bot: AutoShardedBot, tunnel: SSHTunnelForwarder, db: str=None):
    await Tortoise.init(
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "database": db or bot.config["DB_NAME"],
                        "host": bot.config["DB_HOST"],
                        "password": bot.config["DB_PASSWORD"],
                        "port": tunnel.local_bind_port,
                        "user": bot.config["DB_USERNAME"],
                        "schema": bot.config["DB_SCHEMA"],
                    },
                }
            },
            "apps": {
                "main": {"models": _models, "default_connection": "default"}
            },
        }
    )
    conn = Tortoise.get_connection('default')
    await conn.execute_script("""
    DROP TABLE IF EXISTS guild_clusters CASCADE;
    DROP TABLE IF EXISTS guilds CASCADE;
    DROP TABLE IF EXISTS users CASCADE;
    DROP TABLE IF EXISTS banks CASCADE;
    DROP TABLE IF EXISTS guild_infos CASCADE;
    DROP TABLE IF EXISTS cluster_infos CASCADE;
    DROP TABLE IF EXISTS bank_accounts CASCADE;
    DROP TABLE IF EXISTS bank_operations CASCADE;
    DROP TABLE IF EXISTS bank_infos CASCADE;""")

    # Generate the schema
    await Tortoise.generate_schemas()

    return True