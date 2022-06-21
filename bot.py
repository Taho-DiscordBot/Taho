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
import asyncio
from discord.ext import commands 
import discord
from tortoise import Tortoise, run_async
import config
from taho.babel import Babel, _
from taho.utils import TahoContext, init_ssh_tunnel
from taho.database import init_db
import os
from typing import TYPE_CHECKING

import logging
fmt = logging.Formatter(
    fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
sh = logging.FileHandler(filename='logs/tortoise.log', encoding='utf-8', mode='w')
sh.setLevel(logging.DEBUG)
sh.setFormatter(fmt)

logger_tortoise = logging.getLogger("tortoise")
logger_tortoise.setLevel(logging.DEBUG)
logger_tortoise.addHandler(sh)

if TYPE_CHECKING:
    from sshtunnel import SSHTunnelForwarder

class Bot(commands.AutoShardedBot):
    def __init__(self, intents: discord.Intents, **kwargs):
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
        for cog in config.cogs:
            try:
                await self.load_extension(cog)
            except Exception as exc:
                print(f'Could not load extension {cog} due to {exc.__class__.__name__}: {exc}')
        
        # The SSH Tunnel will start only if configured
        self.start_ssh_server()

        # Database initialization
        await init_db(self, self.ssh_server)
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




if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    bot = Bot(intents=intents)

    babel = Babel(bot)
    babel.load()

    try:
        bot.run(config.token)
    except Exception as e:
        raise e
    finally:
        asyncio.set_event_loop(asyncio.new_event_loop())
        run_async(Tortoise.close_connections())
        bot.stop_ssh_server()
        asyncio.get_event_loop().close()
        print("finish")

