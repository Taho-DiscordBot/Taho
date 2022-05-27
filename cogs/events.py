from discord.ext import commands
import discord
from taho.database.models import Guild
from tortoise.exceptions import IntegrityError

class Events(commands.Cog):
    """The description for Events goes here."""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild:discord.Guild):
        try:
            await Guild.create(id=guild.id)
        except IntegrityError:
            pass

async def setup(bot):
    await bot.add_cog(Events(bot))
