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
from taho import forms, utils, _, views, ngettext, BaseView
from taho.database import Currency
from taho.exceptions import AlreadyExists

if TYPE_CHECKING:
    from typing import List, Literal, Optional
    from taho import Bot, TahoContext
    from discord.abc import Snowflake

class CurrencyActionChoiceView(BaseView):
    def __init__(self, user: Optional[Snowflake] = None, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        self.value: Literal["create", "delete", "edit", "list"] = None

        actions = {
            "create": _("Create a currency"),
            "edit": _("Edit an existing currency"),
            "delete": _("Delete an existing currency"),
            "list": _("List all currencies"),
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

class CurrencyChoiceView(BaseView):
    def __init__(self, currencies: List[Currency], user: Optional[Snowflake] = None, multiple: bool = False):
        super().__init__(user)

        self.value: Currency = None
        self.multiple = multiple

        choices = [
            forms.Choice(
                label=currency.name,
                value=currency,
                emoji=currency.emoji
            ) for currency in currencies
        ]

        self.choices_map = {
            choice.discord_value: choice.value for choice in choices
        }

        choices_list = utils.split_list(choices, 25)

        if len(choices_list) > 5:
            return #todo choices_list too long

        self.selects = [
            Select(
                placeholder=_("Select a currency"),
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
                _("Please select only one currency."),
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

class CurrencyCog(commands.Cog):
    """The description for Currency goes here."""

    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def get_currency_form(
        self, 
        ctx: TahoContext, 
        currency: Currency=None, 
        currency_dict: dict=None,
        is_info: bool=False
        ) -> forms.Form:
        """|coro|
        
        Get a form to create or edit a currency.
        The form will be prefilled with the information
        from ``currency`` if given.

        Parameters
        -----------
        ctx: :class:`TahoContext`
            The context of the command.
        currency: Optional[:class:`~taho.database.models.Currency`]
            The currency to prefill the form with.
        currency_dict: Optional[:class:`dict`]
            The currency to prefill the form with.
        is_info: :class:`bool`
            Whether the form is for info or not.
            If ``True``, the form will not be editable.

            Defaults to ``False``.
        
        Raises
        -------
        TypeError
            If both ``currency`` and ``currency_dict`` are given.
            If ``is_info`` is ``True`` and neither ``currency`` nor ``currency_dict`` are given.
        
        Returns
        --------
        :class:`~taho.forms.Form`
            The form to create or edit a currency.
        """
        if currency and currency_dict:
            raise TypeError("Cannot prefill form with both currency and currency_dict.")
        elif is_info and not (currency or currency_dict):
            raise TypeError("Cannot get info form without currency or currency_dict.")
        cluster = await ctx.get_cluster()
        raw_forbidden_values = await cluster.currencies.all().values_list("name", "symbol", "code")
        forbidden_values = {
            "name": [value[0] for value in raw_forbidden_values],
            "symbol": [value[1] for value in raw_forbidden_values],
            "code": [value[2] for value in raw_forbidden_values]
        }
        

        if currency:
            fields_default = await currency.to_dict()
        elif currency_dict:
            fields_default = currency_dict
        else:
            fields_default = None

        fields: List[forms.Field] = [
            forms.Text(
                name="name",
                label=_("Name"),
                description=_("The name of the currency (ex: Dollar)"),
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
                description=_("The symbol of the currency (ex: $)"),
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
                description=_("The code of the currency (ex: USD)"),
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
                description=_("The emoji of the currency (ex: :dollar:)"),
                required=False,
            ),
            forms.Number(
                name="exchange_rate",
                label=_("Exchange rate"),
                description=_("The exchange rate of the currency (ex: 1.0)"),
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
                description=_("Whether the currency is the default currency or not."),
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
                    "Whether the currency supports cash or not. If yes, it will create "
                    "an item, named like the currency, that can be stored in inventories."
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
                form_title = _("Edit %(currency_name)s", currency_name=fields_default["name"])

            for field in fields:
                if field.name == "supports_cash":
                    field.description = _(
                    "Whether the currency supports cash or not. If yes, it will create "
                    "an item, named like the currency, that can be stored in inventories.\n\n"
                    ":warning: If you change this value from **Yes** to **No**, the "
                    "current item used for cash will be deleted."
                    )
                    supports_cash = fields_default.get("item", False)
                    await field.set_value(bool(supports_cash))
                else:
                    await field.set_value(fields_default.get(field.name, None))
        else:
            form_title = _("Create a currency")
    
        form = forms.Form(
            title=form_title,
            fields=fields,
            is_info=is_info,
        )
        return form

    @commands.hybrid_command(
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
    async def currency(self, ctx: TahoContext, action: Choice[str] = None):
        if not action:
            view = CurrencyActionChoiceView(user=ctx.author)
            await ctx.send(view=view)
            await view.wait(delete_after=True)

            if view.value is None:
                return
            
            action = view.value
        
        cluster = await ctx.get_cluster()

        if action == "create":
            
            form = await self.get_currency_form(ctx)
                
            await form.send(ctx=ctx)

            await form.wait()

            if form.is_canceled():
                return
            
            try:
                currency = await cluster.create_currency(**form.to_dict())
            except AlreadyExists as e:
                await ctx.send(e.message, ephemeral=True)
        
            await ctx.send(
                content=_(
                "You have successfully created the currency **%(currency_display)s**.",
                currency_display=str(currency)
                ),
                ephemeral=True
            )

        elif action == "edit":
            currencies = await cluster.currencies.all()

            if not currencies:
                await ctx.send(
                    _("There are no currencies to edit."),
                    ephemeral=True
                )
                return
            
            view = CurrencyChoiceView(currencies, user=ctx.author)
            await ctx.send(view=view)

            await view.wait(delete_after=True)
            currency = view.value

            if not currency:
                return
            
            currency_dict = await currency.to_dict(to_edit=True)
            
            form = await self.get_currency_form(ctx, currency_dict=currency_dict)
            await form.send(ctx=ctx)
            await form.wait()

            if form.is_canceled():
                return

            await currency.edit(**form.to_dict())
        
            await ctx.send(
                content=_(
                    "You have successfully edited the currency **%(currency_display)s**.",
                    currency_display=str(currency)
                ),
                ephemeral=True
            )

        elif action == "delete":
            currencies = await cluster.currencies.all()

            if not currencies:
                await ctx.send(
                    _("There are no currencies to delete."),
                    ephemeral=True
                )
                return
            
            view = CurrencyChoiceView(currencies, user=ctx.author, multiple=True)
            await ctx.send(view=view)

            await view.wait(delete_after=True)
            currencies = view.value

            if not currencies:
                return
            
            currencies_display = ", ".join(str(currency) for currency in currencies) if len(currencies) > 1\
                else str(currencies[0])
            
            confirmation = views.ConfirmationView(user=ctx.author)
            msg = await ctx.send(
                ngettext(
                    "Are you sure you want to delete the currency **%(currency)s**?",
                    "Are you sure you want to delete the currencies **%(currency)s**?",
                    num=len(currencies),
                    currency=currencies_display
                ),
                view=confirmation
                )

            await confirmation.wait()
            await msg.delete(delay=0)
            if confirmation.value is False:
                return
            
            await Currency.filter(id__in=[currency.id for currency in currencies]).delete()
            
            await ctx.send(
                ngettext(
                    "You have successfully deleted the currency **%(currency)s**.",
                    "You have successfully deleted the currencies **%(currency)s**.",
                    num=len(currencies),
                    currency=currencies_display
                ),
                ephemeral=True
            )

        elif action == "list":
            currencies = await cluster.currencies.all()

            if not currencies:
                await ctx.send(
                    _("There are no currencies to list."),
                    ephemeral=True
                )
                return

            content = _(
                "Here is a list of all currencies, select a currency in the selects "
                "below to get more information about it.\n\n"
                "%(currencies)s",
                currencies="\n".join(currency.get_display(long=True) for currency in currencies)
            )
            view = CurrencyChoiceView(currencies, user=ctx.author)
            msg = await ctx.send(content=content, view=view)

            await view.wait()

            currency = view.value

            if not currency:
                await msg.edit(view=None)
                return
            
            await msg.delete(delay=0)

            currency_dict = await currency.to_dict()

            form = await self.get_currency_form(ctx, currency_dict=currency_dict, is_info=True)

            await form.send(ctx=ctx, ephemeral=True)
            

async def setup(bot: Bot):
    await bot.add_cog(CurrencyCog(bot))
