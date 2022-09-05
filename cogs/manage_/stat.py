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
from discord import SelectOption
from discord.app_commands import Choice
from discord.ui import Select
from taho import forms, utils, _, views, ngettext, BaseView
from taho.database import Stat
from taho.exceptions import AlreadyExists

if TYPE_CHECKING:
    from typing import List, Literal, Optional
    from taho import Bot, TahoContext
    from discord.abc import Snowflake

__all__ = (
    "ManageStat",
)

class StatActionChoiceView(BaseView):
    def __init__(self, user: Optional[Snowflake] = None, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        self.value: Literal["create", "delete", "edit", "list"] = None

        actions = {
            "create": _("Create a stat"),
            "edit": _("Edit an existing stat"),
            "delete": _("Delete an existing stat"),
            "list": _("List all stats"),
        }

        self.select = Select(
            placeholder=_("Select an action"),
            options=[
                SelectOption(
                    label=label,
                    value=value
                ) for value, label in actions.items()
            ]
        )
        self.add_item(self.select)
        self.select.callback = self.select_callback
    
    async def select_callback(self, interaction: discord.Interaction):
        self.value = self.select.values[0]
        await interaction.response.defer(ephemeral=True)
        self.stop()

class StatChoiceView(BaseView):
    def __init__(self, stats: List[Stat], user: Optional[Snowflake] = None, multiple: bool = False):
        super().__init__(user)

        self.value: Stat = None
        self.multiple = multiple

        choices = [
            forms.Choice(
                label=stat.name,
                value=stat,
                emoji=stat.emoji
            ) for stat in stats
        ]

        self.choices_map = {
            choice.discord_value: choice.value for choice in choices
        }

        choices_list = utils.split_list(choices, 25)

        if len(choices_list) > 5:
            return #todo choices_list too long

        self.selects = [
            Select(
                placeholder=_("Select a stat"),
                options=choices,
                max_values=1 if not self.multiple else len(choices)
            ) for choices in choices_list
        ]

        for select in self.selects:
            self.add_item(select)
            select.callback = self.select_callback

    
    async def select_callback(self, interaction: discord.Interaction):
        values = []
        for select in self.selects:
            values.extend(select.values)
        
        if len(values) > 1 and not self.multiple:
            await interaction.response.send_message(
                _("Please select only one stat."),
                ephemeral=True
            )
        else:
            if self.multiple:
                self.value = [
                    self.choices_map[value] for value in values
                ]
            else:
                self.value = self.choices_map[values[0]]

            await interaction.response.defer(ephemeral=True)
            self.stop()

class ManageStat:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def get_stat_form(
        self, 
        ctx: TahoContext, 
        stat: Stat=None, 
        stat_dict: dict=None,
        is_info: bool=False
        ) -> forms.Form:
        """|coro|
        
        Get a form to create or edit a stat.
        The form will be prefilled with the information
        from ``stat`` if given.

        Parameters
        -----------
        ctx: :class:`TahoContext`
            The context of the command.
        stat: Optional[:class:`~taho.database.models.Stat`]
            The stat to prefill the form with.
        stat_dict: Optional[:class:`dict`]
            The stat to prefill the form with.
        is_info: :class:`bool`
            Whether the form is for info or not.
            If ``True``, the form will not be editable.

            Defaults to ``False``.
        
        Raises
        -------
        TypeError
            If both ``stat`` and ``stat_dict`` are given.
            If ``is_info`` is ``True`` and neither ``stat`` nor ``stat_dict`` are given.
        
        Returns
        --------
        :class:`~taho.forms.Form`
            The form to create or edit a stat.
        """
        if stat and stat_dict:
            raise TypeError("Cannot prefill form with both stat and stat_dict.")
        elif is_info and not (stat or stat_dict):
            raise TypeError("Cannot get info form without stat or stat_dict.")
        cluster = await ctx.get_cluster()
        raw_forbidden_values = await cluster.stats.all().values_list("name", "symbol", "code")
        forbidden_values = {
            "name": [value[0] for value in raw_forbidden_values],
            "symbol": [value[1] for value in raw_forbidden_values],
            "code": [value[2] for value in raw_forbidden_values]
        }
        

        if stat:
            fields_default = await stat.to_dict()
        elif stat_dict:
            fields_default = stat_dict
        else:
            fields_default = None

        fields: List[forms.Field] = [
            forms.Text(
                name="name",
                label=_("Name"),
                description=_("The name of the stat (ex: Dollar)"),
                required=True,
                max_length=32,
                min_length=3,
                validators=[
                    lambda x: forms.required(x),
                    lambda x: forms.min_length(x, 3),
                    lambda x: forms.max_length(x, 32),
                    lambda x: forms.forbidden_value(x, *forbidden_values["name"]),
                ]
            ),
            forms.Text(
                name="symbol",
                label=_("Symbol"),
                description=_("The symbol of the stat (ex: $)"),
                required=False,
                max_length=8,
                min_length=1,
                validators=[
                    lambda x: forms.min_length(x, 1),
                    lambda x: forms.max_length(x, 8),
                    lambda x: forms.forbidden_value(x, *forbidden_values["symbol"]),
                ]
            ),
            forms.Text(
                name="code",
                label=_("Code"),
                description=_("The code of the stat (ex: USD)"),
                required=True,
                max_length=8,
                min_length=3,
                validators=[
                    lambda x: forms.required(x),
                    lambda x: forms.min_length(x, 3),
                    lambda x: forms.max_length(x, 8),
                    lambda x: forms.forbidden_value(x, *forbidden_values["code"]),
                ]
            ),
            forms.Emoji(
                name="emoji",
                label=_("Emoji"),
                description=_("The emoji of the stat (ex: :dollar:)"),
                required=False,
            ),
            forms.Number(
                name="exchange_rate",
                label=_("Exchange rate"),
                description=_("The exchange rate of the stat (ex: 1.0)"),
                required=True,
                min_value=0,
                validators=[
                    lambda x: forms.required(x),
                    lambda x: forms.min_value(x, 0),
                ]
            ),
            forms.Select(
                name="is_default",
                label=_("Is default"),
                description=_("Whether the stat is the default stat or not."),
                required=True,
                choices=[
                    forms.Choice(
                        label=_("Yes"),
                        value=True,
                        emoji="✅"
                    ),
                    forms.Choice(
                        label=_("No"),
                        value=False,
                        emoji="❌"
                    )
                ],
            ),
            forms.Select(
                name="supports_cash",
                label=_("Supports cash"),
                description=_(
                    "Whether the stat supports cash or not. If yes, it will create "
                    "an item, named like the stat, that can be stored in inventories."
                ),
                required=True,
                choices=[
                    forms.Choice(
                        label=_("Yes"),
                        value=True,
                        emoji="✅"
                    ),
                    forms.Choice(
                        label=_("No"),
                        value=False,
                        emoji="❌"
                    )
                ]
            )
        ]
        if fields_default:
            if is_info:
                form_title = fields_default["name"]
            else:
                form_title = _("Edit %(stat_name)s", stat_name=fields_default["name"])

            for field in fields:
                if field.name == "supports_cash":
                    field.description = _(
                    "Whether the stat supports cash or not. If yes, it will create "
                    "an item, named like the stat, that can be stored in inventories.\n\n"
                    ":warning: If you change this value from **Yes** to **No**, the "
                    "current item used for cash will be deleted."
                    )
                    supports_cash = fields_default.get("item", False)
                    await field.set_value(bool(supports_cash))
                else:
                    await field.set_value(fields_default.get(field.name, None))
        else:
            form_title = _("Create a stat")
    
        form = forms.Form(
            title=form_title,
            fields=fields,
            is_info=is_info,
        )
        return form

    async def callback(self, ctx: TahoContext, action: Choice[str] = None):
        if not action:
            view = StatActionChoiceView(user=ctx.author)
            await ctx.send(view=view)
            await view.wait(delete_after=True)

            if view.value is None:
                return
            
            action = view.value
        
        cluster = await ctx.get_cluster()

        if action == "create":
            
            form = await self.get_stat_form(ctx)
                
            await form.send(ctx=ctx)

            await form.wait()

            if form.is_canceled():
                return
            
            try:
                stat = await cluster.create_stat(**form.to_dict())
            except AlreadyExists as e:
                await ctx.send(e.message, ephemeral=True)
        
            await ctx.send(
                content=_(
                "You have successfully created the stat **%(stat_display)s**.",
                stat_display=str(stat)
                ),
                ephemeral=True
            )

        elif action == "edit":
            stats = await cluster.stats.all()

            if not stats:
                await ctx.send(
                    _("There are no stats to edit."),
                    ephemeral=True
                )
                return
            
            view = StatChoiceView(stats, user=ctx.author)
            await ctx.send(view=view)

            await view.wait(delete_after=True)
            stat = view.value

            if not stat:
                return
            
            stat_dict = await stat.to_dict(to_edit=True)
            
            form = await self.get_stat_form(ctx, stat_dict=stat_dict)
            await form.send(ctx=ctx)
            await form.wait()

            if form.is_canceled():
                return

            await stat.edit(**form.to_dict())
        
            await ctx.send(
                content=_(
                    "You have successfully edited the stat **%(stat_display)s**.",
                    stat_display=str(stat)
                ),
                ephemeral=True
            )

        elif action == "delete":
            stats = await cluster.stats.all()

            if not stats:
                await ctx.send(
                    _("There are no stats to delete."),
                    ephemeral=True
                )
                return
            
            view = StatChoiceView(stats, user=ctx.author, multiple=True)
            await ctx.send(view=view)

            await view.wait(delete_after=True)
            stats = view.value

            if not stats:
                return
            
            stats_display = ", ".join(str(stat) for stat in stats) if len(stats) > 1\
                else str(stats[0])
            
            confirmation = views.ConfirmationView(user=ctx.author)
            msg = await ctx.send(
                ngettext(
                    "Are you sure you want to delete the stat **%(stat)s**?",
                    "Are you sure you want to delete the stats **%(stat)s**?",
                    num=len(stats),
                    stat=stats_display
                ),
                view=confirmation
                )

            await confirmation.wait()
            await msg.delete(delay=0)
            if confirmation.value is False:
                return
            
            await Stat.filter(id__in=[stat.id for stat in stats]).delete()
            
            await ctx.send(
                ngettext(
                    "You have successfully deleted the stat **%(stat)s**.",
                    "You have successfully deleted the stats **%(stat)s**.",
                    num=len(stats),
                    stat=stats_display
                ),
                ephemeral=True
            )

        elif action == "list":
            stats = await cluster.stats.all()

            if not stats:
                await ctx.send(
                    _("There are no stats to list."),
                    ephemeral=True
                )
                return

            content = _(
                "Here is a list of all stats, select a stat in the selects "
                "below to get more information about it.\n\n"
                "%(stats)s",
                stats="\n".join(stat.get_display(long=True) for stat in stats)
            )
            view = StatChoiceView(stats, user=ctx.author)
            msg = await ctx.send(content=content, view=view)

            await view.wait()

            stat = view.value

            if not stat:
                await msg.edit(view=None)
                return
            
            await msg.delete(delay=0)

            stat_dict = await stat.to_dict()

            form = await self.get_stat_form(ctx, stat_dict=stat_dict, is_info=True)

            await form.send(ctx=ctx, ephemeral=True)
     
