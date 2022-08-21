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

if TYPE_CHECKING:
    from typing import List, Literal, Optional
    from taho import Bot, TahoContext
    from discord.abc import Snowflake

class ItemActionChoiceView(BaseView):
    def __init__(self, user: Optional[Snowflake] = None, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        self.value: Literal["create", "delete", "edit", "list"] = None
        super().__init__()

        actions = {
            "create": _("Create an item"),
            "delete": _("Delete an existing item"),
            "edit": _("Edit an existing item"),
            "list": _("List all items"),
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

class ItemChoiceView(BaseView):
    def __init__(self, items: List[Item], user: Optional[Snowflake] = None, multiple: bool = False):
        super().__init__(user)

        self.value: Item = None
        self.multiple = multiple
        super().__init__()

        choices = [
            forms.Choice(
                label=item.name,
                value=item,
                emoji=item.emoji
            ) for item in items
        ]

        self.choices_map = {
            choice.discord_value: choice.value for choice in choices
        }

        choices_list = utils.split_list(choices, 25)

        if len(choices_list) > 5:
            return #todo choices_list too long

        self.selects = [
            Select(
                placeholder=_("Select an item"),
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
                _("Please select only one item."),
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

class ItemCog(commands.Cog):
    """The description for Item goes here."""

    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def get_item_form(
        self, 
        ctx: TahoContext, 
        item: Item=None, 
        item_dict: dict=None,
        is_info: bool=False
        ) -> forms.Form:
        """|coro|
        
        Get a form to create or edit an item.
        The form will be prefilled with the information
        from ``item`` if given.

        Parameters
        -----------
        ctx: :class:`TahoContext`
            The context of the command.
        item: Optional[:class:`~taho.database.models.Item`]
            The item to prefill the form with.
        item_dict: Optional[:class:`dict`]
            The item to prefill the form with.
        is_info: :class:`bool`
            Whether the form is for info or not.
            If ``True``, the form will not be editable.

            Defaults to ``False``.
        
        Raises
        -------
        TypeError
            If both ``item`` and ``item_dict`` are given.
            If ``is_info`` is ``True`` and neither ``item`` nor ``item_dict`` are given.
        
        Returns
        --------
        :class:`~taho.forms.Form`
            The form to create or edit an item.
        """
        if item and item_dict:
            raise TypeError("Cannot prefill form with both item and item_dict.")
        elif is_info and not (item or item_dict):
            raise TypeError("Cannot get info form without item or item_dict.")
        cluster = await ctx.get_cluster()
        forbidden_names = await cluster.items.all().values_list("name", flat=True)

        if item:
            fields_default = await item.to_dict()
        elif item_dict:
            fields_default = item_dict

        fields: List[forms.Field] = [
            forms.Text(
                name="name",
                label=_("Name"),
                description=_("The name of the item"),
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
                description=_("The emoji of the item"),
                required=False
            ),
            forms.Text(
                name="description",
                label=_("Description"),
                description=_("The description of the item"),
                required=False,
                validators=[
                    lambda x: forms.min_length(x, 3),
                    lambda x: forms.max_length(x, 100),
                ]
            ),
            forms.Select(
                name="type",
                label=_("Type"),
                required=True,
                choices=[
                    forms.Choice(
                        label=_("Resource"),
                        value=ItemType.resource,
                        description=_("Resources are the basic items."),
                    ),
                    forms.Choice(
                        label=_("Consumable"),
                        value=ItemType.consumable,
                        description=_("Consumables have durability and can be used."),
                    ),
                    forms.Choice(
                        label=_("Currency"),
                        value=ItemType.currency,
                        description=_("Currency items are used as Cash for a specific Currency."),
                    ),
                ],
                validators=[
                    lambda x: forms.required(x),
                ],
            ),
            forms.Currency(
                cluster_id=cluster.id,
                db_filters={
                    "item__id__isnull": True
                } if not fields_default else {
                    "item__id__in": [
                        fields_default["id"],
                        None
                    ]
                },
                name="currency",
                label=_("Currency"),
                required=True,
                validators=[
                    lambda x: forms.required(x),
                ],
                appear_validators=[
                    lambda f: f["type"] == ItemType.currency,
                ],

            ),
            forms.Number(
                name="durability",
                label=_("Durability"),
                required=True,
                validators=[
                    lambda x: forms.required(x),
                    lambda x: forms.is_int(x),
                    lambda x: forms.min_value(x, -1),
                    lambda x: forms.forbidden_value(x, 0),
                ],
                appear_validators=[
                    lambda f: f["type"] == ItemType.consumable,
                ]
            ),
            forms.Number(
                name="cooldown",
                label=_("Cooldown"),
                required=True,
                validators=[
                    lambda x: forms.is_number(x),
                    lambda x: forms.min_value(x, 0),
                ],
                appear_validators=[
                    lambda f: f["type"] == ItemType.consumable,
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
                reward_types=[
                    {
                        "reward_types": [RewardType.passive,RewardType.active,RewardType.equip],
                        "conditions": [lambda f: f["type"] == ItemType.consumable],
                    },
                    {
                        "reward_types": [RewardType.passive],
                        "conditions": [lambda f: f["type"] in (ItemType.resource, ItemType.currency)],
                    }
                ],
                appear_validators=[
                    lambda f: f["type"] is not None,
                ]
            )
        ]
        if fields_default:
            if is_info:
                form_title = fields_default["name"]
            else:
                form_title = _("Edit %(item_name)s", item_name=fields_default["name"])


            for field in fields:
                await field.set_value(fields_default.get(field.name, None))
        else:
            form_title = _("Create an item")
    
        form = forms.Form(
            title=form_title,
            fields=fields,
            is_info=is_info,
        )
        return form

    @commands.hybrid_command(
        name=_d("item"),
        description=_d("Manage items")
    )
    @utils.check_perm(manage_item=True)
    @app_commands.choices(
        action=[
            Choice(name=_d("Create an item"), value="create"),
            Choice(name=_d("Delete an existing item"), value="delete"),
            Choice(name=_d("Edit an existing item"), value="edit"),
            Choice(name=_d("List all items"), value="list")
        ]
    )
    @app_commands.describe(
        action=_d("Select an action"),
    )
    @app_commands.rename(
        action=_d("action")
    )
    async def item(self, ctx: TahoContext, action: Choice[str] = None):
        if not action:
            view = ItemActionChoiceView()
            msg = await ctx.send(view=view, ephemeral=True)
            await view.wait()
            await msg.delete(delay=0)


            if view.value is None:
                return
            
            action = view.value
        
        cluster = await ctx.get_cluster()

        if action == "create":
            
            form = await self.get_item_form(ctx)
                
            await form.send(ctx=ctx)

            await form.wait()

            if form.is_canceled():
                return

            item = await cluster.create_item(**form.to_dict())
        
            await ctx.send(
                content=_(
                "You have successfully created the item **%(item_display)s**.",
                item_display=str(item)
                ),
                ephemeral=True
            )

        elif action == "edit":
            items = await cluster.items.all()

            if not items:
                await ctx.send(
                    _("There are no items to edit."),
                    ephemeral=True
                )
                return
            
            view = ItemChoiceView(items, user=ctx.author)
            await ctx.send(view=view)

            await view.wait(delete_after=True)
            item = view.value

            if not item:
                return
            
            item_dict = await item.to_dict(to_edit=True)
            
            form = await self.get_item_form(ctx, item_dict=item_dict)
            await form.send(ctx=ctx)
            await form.wait()

            if form.is_canceled():
                return

            await item.edit(**form.to_dict())
        
            await ctx.send(
                content=_(
                    "You have successfully edited the item **%(item_display)s**.",
                    item_display=str(item)
                ),
                ephemeral=True
            )

        elif action == "delete":
            items = await cluster.items.all()

            if not items:
                await ctx.send(
                    _("There are no items to delete."),
                    ephemeral=True
                )
                return
            
            view = ItemChoiceView(items, user=ctx.author, multiple=True)
            await ctx.send(view=view)

            await view.wait(delete_after=True)
            items = view.value

            if not items:
                return
            
            items_display = ", ".join(str(item) for item in items) if len(items) > 1\
                else str(items[0])
            
            confirmation = views.ConfirmationView(user=ctx.author)
            msg = await ctx.send(
                ngettext(
                    "Are you sure you want to delete the item **%(item)s**?",
                    "Are you sure you want to delete the items **%(item)s**?",
                    num=len(items),
                    item=items_display
                ),
                view=confirmation,
                ephemeral=True
                )

            await confirmation.wait()
            await msg.delete(delay=0)
            if confirmation.value is False:
                return
            
            await Item.filter(id__in=[item.id for item in items]).delete()
            
            await ctx.send(
                ngettext(
                    "You have successfully deleted the item **%(item)s**.",
                    "You have successfully deleted the items **%(item)s**.",
                    num=len(items),
                    item=items_display
                ),
                ephemeral=True
            )

        elif action == "list":
            items = await cluster.items.all()

            if not items:
                await ctx.send(
                    _("There are no items to list."),
                    ephemeral=True
                )
                return

            content = _(
                "Here is a list of all items, select an item in the selects "
                "below to get more information about it.\n\n"
                "%(items)s",
                items="\n".join(item.get_display(long=True) for item in items)
            )
            view = ItemChoiceView(items, user=ctx.author)
            msg = await ctx.send(content=content, view=view, ephemeral=True)

            await view.wait()

            item = view.value

            if not item:
                await msg.edit(view=None)
                return
            
            await msg.delete(delay=0)

            item_dict = await item.to_dict()

            form = await self.get_item_form(ctx, item_dict=item_dict, is_info=True)

            await form.send(ctx=ctx, ephemeral=True)
            

async def setup(bot: Bot):
    await bot.add_cog(ItemCog(bot))
