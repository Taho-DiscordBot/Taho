from discord.ext.commands import AutoShardedBot
import discord


intents = discord.Intents.default()
intents.message_content = True
bot = AutoShardedBot("!", intents=intents)