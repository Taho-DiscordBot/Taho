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
from tortoise import Tortoise
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sshtunnel import SSHTunnelForwarder


_models = [
    "taho.database.models.bank",
    "taho.database.models.channel",
    "taho.database.models.class_",
    "taho.database.models.cluster",
    "taho.database.models.currency",
    "taho.database.models.inventory",
    "taho.database.models.item",
    "taho.database.models.job",
    "taho.database.models.npc",
    "taho.database.models.role",
    "taho.database.models.server",
    "taho.database.models.shortcut",
    "taho.database.models.stat",
    "taho.database.models.user",
    ]

async def init_db(config: dict, ssh_tunnel: SSHTunnelForwarder=None, _create_db: bool=False) -> None:
    """|coro|

    Connect and initialize the database.

    Parameters
    ----------
    config: :class:`dict`
        The config dictionary, which is loaded from 
        the config file.
    tunnel: Optional[:class:`sshtunnel.SSHTunnelForwarder`]
        The SSH tunnel instance if used.
    _create_db: Optional[bool]
        Whether to create the database.
        Only for testing purposes.
    """
    # If the SSH tunnel is not used, we can use the default port
    # The SSH tunnel creates a new port for the DB
    port = ssh_tunnel.local_bind_port if ssh_tunnel else config["DB_PORT"]
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