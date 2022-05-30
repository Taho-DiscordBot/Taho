from __future__ import annotations
import asyncio
from discord.ext import commands 
import discord
from tortoise import Tortoise, run_async
import config
from taho.babel import Babel, _
from taho.utils import TahoContext
from taho.database import init_db
import os
from typing import TYPE_CHECKING

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
        from sshtunnel import SSHTunnelForwarder
        self.ssh_server: SSHTunnelForwarder = SSHTunnelForwarder(
            (self.config["SSH_HOST"], self.config["SSH_PORT"]),
            ssh_username=self.config["SSH_USERNAME"],
            ssh_password=self.config["SSH_PASSWORD"],
            remote_bind_address=(self.config["SSH_REMOTE_HOST"], self.config["SSH_REMOTE_PORT"]),
        )
        self.ssh_server.start()
        return True
    
    def stop_ssh_server(self):
        self.ssh_server.stop()
        return True

    async def setup_hook(self):
        for cog in config.cogs:
            try:
                await self.load_extension(cog)
            except Exception as exc:
                print(f'Could not load extension {cog} due to {exc.__class__.__name__}: {exc}')
        
        self.start_ssh_server()
        await init_db(self, self.ssh_server)

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

