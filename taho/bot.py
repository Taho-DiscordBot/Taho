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
from .utils import init_ssh_tunnel, TahoContext
from .database import init_db

if TYPE_CHECKING:
    from sshtunnel import SSHTunnelForwarder

__all__ = (
    "Bot",
)

class Bot(commands.AutoShardedBot):
    def __init__(self, intents: discord.Intents, config, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('!'), intents=intents, **kwargs)
        self.uptime = discord.utils.utcnow()
        self.config = vars(config)
        self.root_path = os.getcwd()
        self.ssh_server: SSHTunnelForwarder
    
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
        for cog in self.config.get("cogs", []):
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


        MY_GUILD = discord.Object(724535633283907639)
        self.tree.copy_global_to(guild=MY_GUILD)
        #await self.tree.sync(guild=MY_GUILD)

    async def on_ready(self):
        duration = (discord.utils.utcnow() - self.uptime).total_seconds()
        self.uptime = discord.utils.utcnow()
        print(f'Logged on as {self.user} (ID: {self.user.id}) in {len(self.guilds)} guilds and {duration} seconds')

    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=TahoContext)