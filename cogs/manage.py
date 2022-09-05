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
import discord
from discord.ext import commands
from discord import app_commands, SelectOption
from discord.app_commands import Choice, locale_str as _d
from discord.ui import Select
from taho import forms, utils, _, views, ngettext, ItemType, RewardType, BaseView
from taho.database import Item
from .manage_ import *

if TYPE_CHECKING:
    from typing import List, Literal, Optional
    from taho import Bot, TahoContext
    from discord.abc import Snowflake

class Manage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_group(name="manage", invoke_without_command=True)
    async def manage_group(self, ctx):
        await ctx.send_help(ctx.command)
    
    @manage_group.command(
        name=_d("item"),
        description=_d("Manage items")
    )
    @utils.check_perm(manage_item=True)
    @app_commands.choices(
        action=[
            Choice(name=_d("Create an item"), value="create"),
            Choice(name=_d("Edit an existing item"), value="edit"),
            Choice(name=_d("Delete an existing item"), value="delete"),
            Choice(name=_d("List all items"), value="list")
        ]
    )
    @app_commands.describe(
        action=_d("Select an action"),
    )
    @app_commands.rename(
        action=_d("action")
    )
    async def manage_item(self, ctx: TahoContext, action: Choice[str] = None):
        command = ManageItem(self.bot)
        await command.callback(ctx, action.value if action else None)
    
    @manage_group.command(
        name=_d("currency"),
        description=_d("Manage currencies")
    )
    @utils.check_perm(manage_currency=True)
    @app_commands.choices(
        action=[
            Choice(name=_d("Create a currency"), value="create"),
            Choice(name=_d("Edit an existing currency"), value="edit"),
            Choice(name=_d("Delete an existing currency"), value="delete"),
            Choice(name=_d("List all currencies"), value="list")
        ]
    )
    @app_commands.describe(
        action=_d("Select an action"),
    )
    @app_commands.rename(
        action=_d("action")
    )
    async def manage_currency(self, ctx: TahoContext, action: Choice[str] = None):
        command = ManageCurrency(self.bot)
        await command.callback(ctx, action.value if action else None)

    @manage_group.command(
        name=_d("craft"),
        description=_d("Manage crafts")
    )
    @utils.check_perm(manage_craft=True)
    @app_commands.choices(
        action=[
            Choice(name=_d("Create a craft"), value="create"),
            Choice(name=_d("Edit an existing craft"), value="edit"),
            Choice(name=_d("Delete an existing craft"), value="delete"),
            Choice(name=_d("List all crafts"), value="list")
        ]
    )
    @app_commands.describe(
        action=_d("Select an action"),
    )
    @app_commands.rename(
        action=_d("action")
    )
    async def manage_craft(self, ctx: TahoContext, action: Choice[str] = None):
        command = ManageCraft(self.bot)
        await command.callback(ctx, action.value if action else None)
    
    @manage_group.command(
        name=_d("bank"),
        description=_d("Manage banks")
    )
    @utils.check_perm(manage_bank=True)
    @app_commands.choices(
        action=[
            Choice(name=_d("Create a bank"), value="create"),
            Choice(name=_d("Edit an existing bank"), value="edit"),
            Choice(name=_d("Delete an existing bank"), value="delete"),
            Choice(name=_d("List all banks"), value="list")
        ]
    )
    @app_commands.describe(
        action=_d("Select an action"),
    )
    @app_commands.rename(
        action=_d("action")
    )
    async def manage_bank(self, ctx: TahoContext, action: Choice[str] = None):
        command = ManageBank(self.bot)
        await command.callback(ctx, action.value if action else None)
    
    @manage_group.command(
        name=_d("stat"),
        description=_d("Manage stats")
    )
    @utils.check_perm(manage_stat=True)
    @app_commands.choices(
        action=[
            Choice(name=_d("Create a stat"), value="create"),
            Choice(name=_d("Edit an existing stat"), value="edit"),
            Choice(name=_d("Delete an existing stat"), value="delete"),
            Choice(name=_d("List all stats"), value="list")
        ]
    )
    @app_commands.describe(
        action=_d("Select an action"),
    )
    @app_commands.rename(
        action=_d("action")
    )
    async def manage_stat(self, ctx: TahoContext, action: Choice[str] = None):
        command = ManageStat(self.bot)
        await command.callback(ctx, action.value if action else None)
    
    @manage_group.command(
        name=_d("class"),
        description=_d("Manage classes")
    )
    @utils.check_perm(manage_class=True)
    @app_commands.choices(
        action=[
            Choice(name=_d("Create a class"), value="create"),
            Choice(name=_d("Edit an existing class"), value="edit"),
            Choice(name=_d("Delete an existing class"), value="delete"),
            Choice(name=_d("List all classes"), value="list")
        ]
    )
    @app_commands.describe(
        action=_d("Select an action"),
    )
    @app_commands.rename(
        action=_d("action")
    )
    async def manage_class(self, ctx: TahoContext, action: Choice[str] = None):
        command = ManageClass(self.bot)
        await command.callback(ctx, action.value if action else None)

async def setup(bot):
    await bot.add_cog(Manage(bot))
