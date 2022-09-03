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
from taho import forms, utils, _, views, ngettext, RewardType, BaseView, ItemType as CraftType
from taho.database import Craft

if TYPE_CHECKING:
    from typing import List, Literal, Optional
    from taho import Bot, TahoContext
    from discord.abc import Snowflake

class CraftActionChoiceView(BaseView):
    def __init__(self, user: Optional[Snowflake] = None, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        self.value: Literal["create", "delete", "edit", "list"] = None

        actions = {
            "create": _("Create a craft"),
            "edit": _("Edit an existing craft"),
            "delete": _("Delete an existing craft"),
            "list": _("List all crafts"),
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

class CraftChoiceView(BaseView):
    def __init__(self, crafts: List[Craft], user: Optional[Snowflake] = None, multiple: bool = False):
        super().__init__(user)

        self.value: Craft = None
        self.multiple = multiple

        choices = [
            forms.Choice(
                label=craft.name,
                value=craft,
                emoji=craft.emoji
            ) for craft in crafts
        ]

        self.choices_map = {
            choice.discord_value: choice.value for choice in choices
        }

        choices_list = utils.split_list(choices, 25)

        if len(choices_list) > 5:
            return #todo choices_list too long

        self.selects = [
            Select(
                placeholder=_("Select a craft"),
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
                _("Please select only one craft."),
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

class CraftCog(commands.Cog):
    """The description for Craft goes here."""

    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def get_craft_form(
        self, 
        ctx: TahoContext, 
        craft: Craft=None, 
        craft_dict: dict=None,
        is_info: bool=False
        ) -> forms.Form:
        """|coro|
        
        Get a form to create or edit a craft.
        The form will be prefilled with the information
        from ``craft`` if given.

        Parameters
        -----------
        ctx: :class:`TahoContext`
            The context of the command.
        craft: Optional[:class:`~taho.database.models.Craft`]
            The craft to prefill the form with.
        craft_dict: Optional[:class:`dict`]
            The craft to prefill the form with.
        is_info: :class:`bool`
            Whether the form is for info or not.
            If ``True``, the form will not be editable.

            Defaults to ``False``.
        
        Raises
        -------
        TypeError
            If both ``craft`` and ``craft_dict`` are given.
            If ``is_info`` is ``True`` and neither ``craft`` nor ``craft_dict`` are given.
        
        Returns
        --------
        :class:`~taho.forms.Form`
            The form to create or edit a craft.
        """
        if craft and craft_dict:
            raise TypeError("Cannot prefill form with both craft and craft_dict.")
        elif is_info and not (craft or craft_dict):
            raise TypeError("Cannot get info form without craft or craft_dict.")
        cluster = await ctx.get_cluster()
        forbidden_names = await cluster.crafts.all().values_list("name", flat=True)

        if craft:
            fields_default = await craft.to_dict()
        elif craft_dict:
            fields_default = craft_dict
        else:
            fields_default = None

        fields: List[forms.Field] = [
            forms.Text(
                name="name",
                label=_("Name"),
                description=_("The name of the craft"),
                required=True,
                max_length=32,
                min_length=3,
                validators=[
                    lambda x: forms.required(x),
                    lambda x: forms.min_length(x, 3),
                    lambda x: forms.max_length(x, 32),
                    lambda x: forms.forbidden_value(x, *forbidden_names),
                ]
            ),
            forms.Emoji(
                name="emoji",
                label=_("Emoji"),
                description=_("The emoji of the craft"),
                required=False
            ),
            forms.Text(
                name="description",
                label=_("Description"),
                description=_("The description of the craft"),
                required=False,
                validators=[
                    lambda x: forms.min_length(x, 3),
                    lambda x: forms.max_length(x, 100),
                ]
            ),
            forms.Number(
                name="time",
                label=_("Time (**x**)"),
                required=True,
                validators=[
                    lambda x: forms.required(x),
                    lambda x: forms.min_value(x, -1),
                    lambda x: forms.forbidden_value(x, 0),
                ],
            ),
            forms.Number(
                name="per",
                label=_("Per (**y**)"),
                required=True,
                validators=[
                    lambda x: forms.required(x),
                    lambda x: forms.min_value(x, 1),
                ],
                appear_validators=[
                    lambda f: f["time"] not in (None, -1)
                ]
            ),
            forms.AccessRule(
                name="access_rules",
                label=_("Access rules"),
                required=False,
            ),
            forms.Reward(
                name="reward_packs",
                label=_("Rewards"),
                required=False,
            )
        ]
        if fields_default:
            if is_info:
                form_title = fields_default["name"]
            else:
                form_title = _("Edit %(craft_name)s", craft_name=fields_default["name"])


            for field in fields:
                await field.set_value(fields_default.get(field.name, None))
        else:
            form_title = _("Create a craft")

        description = _(
            "Please fill out the form below.\n"
            "You can use the buttons below to navigate the form.\n"
            "A title with `*` indicates a required field, "
            "one with `x` indicates that it cannot be defined.\n"
            "\n\n"
            "ℹ️ **Cooldown explanation:**\n"
            "The cooldown is the time between two crafts. "
            "It is defined by **x** and **y**: you can do the craft "
            "**x** times every **y** seconds (you can find x and y in the form, as *Time* and *Per*).\n"
            "For an infinite cooldown, set **x** to `-1`.\n"
            )
    
        form = forms.Form(
            title=form_title,
            fields=fields,
            is_info=is_info,
            description=description
        )
        return form

    @commands.hybrid_command(
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
    async def craft(self, ctx: TahoContext, action: Choice[str] = None):
        if not action:
            view = CraftActionChoiceView(user=ctx.author)
            await ctx.send(view=view)
            await view.wait(delete_after=True)

            if view.value is None:
                return
            
            action = view.value
        
        cluster = await ctx.get_cluster()

        if action == "create":
            
            form = await self.get_craft_form(ctx)
                
            await form.send(ctx=ctx)

            await form.wait()

            if form.is_canceled():
                return

            craft = await cluster.create_craft(**form.to_dict())
        
            await ctx.send(
                content=_(
                "You have successfully created the craft **%(craft_display)s**.",
                craft_display=str(craft)
                ),
                ephemeral=True
            )

        elif action == "edit":
            crafts = await cluster.crafts.all()

            if not crafts:
                await ctx.send(
                    _("There are no crafts to edit."),
                    ephemeral=True
                )
                return
            
            view = CraftChoiceView(crafts, user=ctx.author)
            await ctx.send(view=view)

            await view.wait(delete_after=True)
            craft = view.value

            if not craft:
                return
            
            craft_dict = await craft.to_dict(to_edit=True)
            
            form = await self.get_craft_form(ctx, craft_dict=craft_dict)
            await form.send(ctx=ctx)
            await form.wait()

            if form.is_canceled():
                return

            await craft.edit(**form.to_dict())
        
            await ctx.send(
                content=_(
                    "You have successfully edited the craft **%(craft_display)s**.",
                    craft_display=str(craft)
                ),
                ephemeral=True
            )

        elif action == "delete":
            crafts = await cluster.crafts.all()

            if not crafts:
                await ctx.send(
                    _("There are no crafts to delete."),
                    ephemeral=True
                )
                return
            
            view = CraftChoiceView(crafts, user=ctx.author, multiple=True)
            await ctx.send(view=view)

            await view.wait(delete_after=True)
            crafts = view.value

            if not crafts:
                return
            
            crafts_display = ", ".join(str(craft) for craft in crafts) if len(crafts) > 1\
                else str(crafts[0])
            
            confirmation = views.ConfirmationView(user=ctx.author)
            msg = await ctx.send(
                ngettext(
                    "Are you sure you want to delete the craft **%(craft)s**?",
                    "Are you sure you want to delete the crafts **%(craft)s**?",
                    num=len(crafts),
                    craft=crafts_display
                ),
                view=confirmation
                )

            await confirmation.wait()
            await msg.delete(delay=0)
            if confirmation.value is False:
                return
            
            await Craft.filter(id__in=[craft.id for craft in crafts]).delete()
            
            await ctx.send(
                ngettext(
                    "You have successfully deleted the craft **%(craft)s**.",
                    "You have successfully deleted the crafts **%(craft)s**.",
                    num=len(crafts),
                    craft=crafts_display
                ),
                ephemeral=True
            )

        elif action == "list":
            crafts = await cluster.crafts.all()

            if not crafts:
                await ctx.send(
                    _("There are no crafts to list."),
                    ephemeral=True
                )
                return

            content = _(
                "Here is a list of all crafts, select a craft in the selects "
                "below to get more information about it.\n\n"
                "%(crafts)s",
                crafts="\n".join(craft.get_display(long=True) for craft in crafts)
            )
            view = CraftChoiceView(crafts, user=ctx.author)
            msg = await ctx.send(content=content, view=view)

            await view.wait()

            craft = view.value

            if not craft:
                await msg.edit(view=None)
                return
            
            await msg.delete(delay=0)

            craft_dict = await craft.to_dict()

            form = await self.get_craft_form(ctx, craft_dict=craft_dict, is_info=True)

            await form.send(ctx=ctx, ephemeral=True)
            

async def setup(bot: Bot):
    await bot.add_cog(CraftCog(bot))
