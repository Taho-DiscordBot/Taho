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
from taho.database import Bank

if TYPE_CHECKING:
    from typing import List, Literal, Optional
    from taho import Bot, TahoContext
    from discord.abc import Snowflake

class BankActionChoiceView(BaseView):
    def __init__(self, user: Optional[Snowflake] = None, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        self.value: Literal["create", "delete", "edit", "list"] = None
        super().__init__()

        actions = {
            "create": _("Create a bank"),
            "edit": _("Edit an existing bank"),
            "delete": _("Delete an existing bank"),
            "list": _("List all banks"),
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

class BankChoiceView(BaseView):
    def __init__(self, banks: List[Bank], user: Optional[Snowflake] = None, multiple: bool = False):
        super().__init__(user)

        self.value: Bank = None
        self.multiple = multiple
        super().__init__()

        choices = [
            forms.Choice(
                label=bank.name,
                value=bank,
                emoji=bank.emoji
            ) for bank in banks
        ]

        self.choices_map = {
            choice.discord_value: choice.value for choice in choices
        }

        choices_list = utils.split_list(choices, 25)

        if len(choices_list) > 5:
            return #todo choices_list too long

        self.selects = [
            Select(
                placeholder=_("Select a bank"),
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
                _("Please select only one bank."),
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

class BankCog(commands.Cog):
    """The description for Bank goes here."""

    def __init__(self, bot: Bot):
        self.bot = bot
    
    async def _get_infos_fields(
        self, 
        ctx: TahoContext, 
        ) -> List[forms.Field]:
        """|coro|
        
        Get a form to create or edit a bank.
        The form will be prefilled with the information
        from ``bank`` if given.

        Parameters
        -----------
        ctx: :class:`TahoContext`
            The context of the command.
        bank: Optional[:class:`~taho.database.models.Bank`]
            The bank to prefill the form with.
        bank_dict: Optional[:class:`dict`]
            The bank to prefill the form with.
        is_info: :class:`bool`
            Whether the form is for info or not.
            If ``True``, the form will not be editable.

            Defaults to ``False``.
        
        Raises
        -------
        TypeError
            If both ``bank`` and ``bank_dict`` are given.
            If ``is_info`` is ``True`` and neither ``bank`` nor ``bank_dict`` are given.
        
        Returns
        --------
        :class:`~taho.forms.Form`
            The form to create or edit a bank.
        """
        cluster = await ctx.get_cluster()
        fields = [
            forms.Select(
                name="allow_currency_exchange",
                label=_("Allow currency exchange"),
                description=_("Can this bank exchange currencies for its customers?"),
                required=True,
                validators=[
                    lambda x: forms.required(x),
                ],
                choices=[
                    forms.Choice(
                        label=_("Yes"),
                        value=True
                    ),
                    forms.Choice(
                        label=_("No"),
                        value=False
                    )
                ]
            ),
            forms.Currency(
                name="allowed_currencies",
                label=_("Allowed currencies"),
                description=_("Accounts can only support these currencies."),
                cluster=cluster.id,
                required=True,
                validators=[
                    lambda x: forms.required(x),
                ],
                max_values=-1
            ),
            forms.Number(
                name="exchange_fee",
                label=_("Exchange fee (as a %% of the amount exchanged)"),
                required=False,
                validators=[
                    lambda x: forms.min_value(x, 0),
                    lambda x: forms.max_value(x, 100)
                ],
                appear_validators=[
                    lambda f: f["allow_currency_exchange"] == True
                ]
            ),
            forms.Number(
                name="account_opening_fees",
                label=_("Account opening fee"),
                required=False,
                validators=[
                    lambda x: forms.min_value(x, 0),
                ],
            ),
            forms.Number(
                name="interests",
                label=_("Interests (as a %% of the balance)"),
                required=False,
                validators=[
                    lambda x: forms.min_value(x, 0),
                    lambda x: forms.max_value(x, 100)
                ],
            ),
            forms.Number(
                name="account_maintenance_fees",
                label=_("Account maintenance fees (recurrent)"),
                required=False,
                validators=[
                    lambda x: forms.min_value(x, 0),
                ],
            ),
            forms.Number(
                name="withdrawal_fee",
                label=_("Withdrawal fee (as a %% of the withdraw)"),
                required=False,
                validators=[
                    lambda x: forms.min_value(x, 0),
                    lambda x: forms.max_value(x, 100)
                ],
            ),
        ]
        return fields

    async def get_bank_form(
        self, 
        ctx: TahoContext, 
        bank: Bank=None, 
        bank_dict: dict=None,
        is_info: bool=False
        ) -> forms.Form:
        """|coro|
        
        Get a form to create or edit a bank.
        The form will be prefilled with the information
        from ``bank`` if given.

        Parameters
        -----------
        ctx: :class:`TahoContext`
            The context of the command.
        bank: Optional[:class:`~taho.database.models.Bank`]
            The bank to prefill the form with.
        bank_dict: Optional[:class:`dict`]
            The bank to prefill the form with.
        is_info: :class:`bool`
            Whether the form is for info or not.
            If ``True``, the form will not be editable.

            Defaults to ``False``.
        
        Raises
        -------
        TypeError
            If both ``bank`` and ``bank_dict`` are given.
            If ``is_info`` is ``True`` and neither ``bank`` nor ``bank_dict`` are given.
        
        Returns
        --------
        :class:`~taho.forms.Form`
            The form to create or edit a bank.
        """
        if bank and bank_dict:
            raise TypeError("Cannot prefill form with both bank and bank_dict.")
        elif is_info and not (bank or bank_dict):
            raise TypeError("Cannot get info form without bank or bank_dict.")
        cluster = await ctx.get_cluster()
        forbidden_names = await cluster.banks.all().values_list("name", flat=True)

        if bank:
            fields_default = await bank.to_dict()
        elif bank_dict:
            fields_default = bank_dict
        else:
            fields_default = None
        
        fields: List[forms.Field] = [
            forms.Text(
                name="name",
                label=_("Name"),
                description=_("The name of the bank"),
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
                description=_("The emoji of the bank"),
                required=False
            ),
            forms.Text(
                name="description",
                label=_("Description"),
                description=_("The description of the bank"),
                required=False,
                validators=[
                    lambda x: forms.min_length(x, 3),
                    lambda x: forms.max_length(x, 100),
                ]
            ),
            forms.Currency(
                name="default_currency",
                label=_("Default currency"),
                description=_("The interests and fees will be converted to this currency."),
                cluster=cluster.id,
                required=True,
                validators=[
                    lambda x: forms.required(x),
                ],
                max_values=1
            ),
            forms.AccessRule(
                name="access_rules",
                label=_("Access rules"),
                required=False,
            ),
            forms.Infos(
                name="infos",
                label="Infos",
                infos_fields=await self._get_infos_fields(ctx),
                required=True,
                validators=[
                    lambda x: forms.required(x)
                ]
            )
        ]
        if fields_default:
            if is_info:
                form_title = fields_default["name"]
            else:
                form_title = _("Edit %(bank_name)s", bank_name=fields_default["name"])


            for field in fields:
                await field.set_value(fields_default.get(field.name, None))
        else:
            form_title = _("Create a bank")
    
        form = forms.Form(
            title=form_title,
            fields=fields,
            is_info=is_info,
        )
        return form

    @commands.hybrid_command(
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
    async def bank(self, ctx: TahoContext, action: Choice[str] = None):
        if not action:
            view = BankActionChoiceView(user=ctx.author)
            await ctx.send(view=view)
            await view.wait(delete_after=True)

            if view.value is None:
                return
            
            action = view.value
        
        cluster = await ctx.get_cluster()

        if action == "create":
            
            form = await self.get_bank_form(ctx)
                
            await form.send(ctx=ctx)

            await form.wait()

            if form.is_canceled():
                return

            bank = await cluster.create_bank(**form.to_dict())
        
            await ctx.send(
                content=_(
                "You have successfully created the bank **%(bank_display)s**.",
                bank_display=str(bank)
                ),
                ephemeral=True
            )

        elif action == "edit":
            banks = await cluster.banks.all()

            if not banks:
                await ctx.send(
                    _("There are no banks to edit."),
                    ephemeral=True
                )
                return
            
            view = BankChoiceView(banks, user=ctx.author)
            await ctx.send(view=view)

            await view.wait(delete_after=True)
            bank = view.value

            if not bank:
                return
            
            bank_dict = await bank.to_dict(to_edit=True)
            
            form = await self.get_bank_form(ctx, bank_dict=bank_dict)
            await form.send(ctx=ctx)
            await form.wait()

            if form.is_canceled():
                return

            await bank.edit(**form.to_dict())
        
            await ctx.send(
                content=_(
                    "You have successfully edited the bank **%(bank_display)s**.",
                    bank_display=str(bank)
                ),
                ephemeral=True
            )

        elif action == "delete":
            banks = await cluster.banks.all()

            if not banks:
                await ctx.send(
                    _("There are no banks to delete."),
                    ephemeral=True
                )
                return
            
            view = BankChoiceView(banks, user=ctx.author, multiple=True)
            await ctx.send(view=view)

            await view.wait(delete_after=True)
            banks = view.value

            if not banks:
                return
            
            banks_display = ", ".join(str(bank) for bank in banks) if len(banks) > 1\
                else str(banks[0])
            
            confirmation = views.ConfirmationView(user=ctx.author)
            msg = await ctx.send(
                ngettext(
                    "Are you sure you want to delete the bank **%(bank)s**?",
                    "Are you sure you want to delete the banks **%(bank)s**?",
                    num=len(banks),
                    bank=banks_display
                ),
                view=confirmation
                )

            await confirmation.wait()
            await msg.delete(delay=0)
            if confirmation.value is False:
                return
            
            await Bank.filter(id__in=[bank.id for bank in banks]).delete()
            
            await ctx.send(
                ngettext(
                    "You have successfully deleted the bank **%(bank)s**.",
                    "You have successfully deleted the banks **%(bank)s**.",
                    num=len(banks),
                    bank=banks_display
                ),
                ephemeral=True
            )

        elif action == "list":
            banks = await cluster.banks.all()

            if not banks:
                await ctx.send(
                    _("There are no banks to list."),
                    ephemeral=True
                )
                return

            content = _(
                "Here is a list of all banks, select a bank in the selects "
                "below to get more information about it.\n\n"
                "%(banks)s",
                banks="\n".join(bank.get_display(long=True) for bank in banks)
            )
            view = BankChoiceView(banks, user=ctx.author)
            msg = await ctx.send(content=content, view=view)

            await view.wait()

            bank = view.value

            if not bank:
                await msg.edit(view=None)
                return
            
            await msg.delete(delay=0)

            bank_dict = await bank.to_dict()

            form = await self.get_bank_form(ctx, bank_dict=bank_dict, is_info=True)

            await form.send(ctx=ctx, ephemeral=True)
            

async def setup(bot: Bot):
    await bot.add_cog(BankCog(bot))
