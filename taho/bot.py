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
from discord.ext import commands
import discord
from tortoise import Tortoise
import os
from .utils import init_ssh_tunnel, TahoContext, register_bot, register_before_invoke
from .database import init_db, models as db_models
from .babel import Babel
from .lazy import lazy_convert

import json


if TYPE_CHECKING:
    from sshtunnel import SSHTunnelForwarder
    from typing import Any, List

__all__ = (
    "Bot",
)

def override_json() -> None:

    def _to_json(obj: Any) -> str:
        obj = lazy_convert(obj)
        return json.dumps(obj, separators=(',', ':'), ensure_ascii=True)

    discord.utils._to_json = _to_json

class Bot(commands.AutoShardedBot):
    def __init__(
        self, 
        intents: discord.Intents, 
        config, 
        sync_tree: bool = False,
        **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('!'), intents=intents, **kwargs)
        self.uptime = discord.utils.utcnow()
        self.config = vars(config)
        self.sync_tree = sync_tree
        self.root_path = os.getcwd()
        self.ssh_server: SSHTunnelForwarder
        self.registered_servers: List[int] = None
        self.babel: Babel = None
    
    def start_ssh_server(self):
        # The ssh server is only stared if wanted
        if self.config.get("USE_SSH_TUNNEL", False):
            self.ssh_server = init_ssh_tunnel(self.config)
            self.ssh_server.start()
        else:
            self.ssh_server = None
        return True
    
    def stop_ssh_server(self):
        if self.config.get("USE_SSH_TUNNEL", False):
            self.ssh_server.stop()
        return True

    async def setup_hook(self):

        # Override the json serializer
        # to make it work with LazyString
        override_json()

        for cog in self.config.get("cogs", []):
            print(f"Loading cog {cog}")
            try:
                await self.load_extension(cog)
            except Exception as exc:
                print(f'Could not load extension {cog} due to {exc.__class__.__name__}: {exc}')
        
        # The SSH Tunnel will start only if configured
        self.start_ssh_server()

        # Database initialization
        await init_db(self.config, ssh_tunnel=self.ssh_server)
        # Generate the schema for the database
        await Tortoise.generate_schemas()
        print("Database successfully connected")


        

        self.registered_servers = await db_models.Server.all().values_list("id", flat=True)

        babel = Babel(self)
        babel.load()

        register_bot(self)
        register_before_invoke(self)

        if self.sync_tree or self.config.get("DEBUG", False):

            if self.config.get("DEBUG", False):
                print("DEBUG is enabled, syncing the tree to the test guilds...")
                guilds = [
                    discord.Object(guild_id) for guild_id in self.config.get("TEST_GUILDS", [])
                ]

                for guild in guilds:

                    self.tree.copy_global_to(guild=guild)

                    await self.tree.sync(guild=guild)

                    print(f"Synced the tree to {guild.id}")
                
                
            else:
                print("Syncing the tree to all guilds...")
                await self.tree.sync()
            
            print("Tree successfully synced")


            

    async def on_ready(self):
        duration = (discord.utils.utcnow() - self.uptime).total_seconds()
        self.uptime = discord.utils.utcnow()
        print(f'Logged on as {self.user} (ID: {self.user.id}) in {len(self.guilds)} guilds and {duration} seconds')

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=TahoContext)
    
    async def on_command_error(self, context, exception, /) -> None:
        raise exception