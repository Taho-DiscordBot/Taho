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
import traceback
from typing import TYPE_CHECKING
from discord import Interaction, ui, SelectOption, ButtonStyle, TextStyle
from taho.babel import _
from taho.utils.utils_ import split_list
from taho.database.models import Item
from .field import Field, FieldView
from ..choice import Choice
from ..validators import is_number
from taho.abstract import AbstractClassStat
from taho.base_view import BaseView
from taho.exceptions import ValidationException

if TYPE_CHECKING:
    from typing import List, Callable, Optional, Dict, Any, Literal
    from taho.database.models import Role

    AccessibleList = List[List[str, Role]]

__all__ = (
    "Stat",
)

class StatView(FieldView):
    def __init__(
        self, 
        field: Stat, 
        ) -> None:
        default = field.value
        super().__init__(field, default)
        self.stat_list = self.field.stat_list
        self.value = self.default

        self.action.placeholder = _("What do you want to do?")
        self.action_options = {
            "add": SelectOption(
                label=_("Add a stat"),
                value="add",
            ),
            "remove": SelectOption(
                label=_("Remove a stat"),
                value="remove",
            ),
        }

        self.finish.label = _("Finish")

        self.check_action_options()
    
    def check_action_options(self) -> None:
        self.value = self.field.value
        if self.value:
            self.action.options = list(self.action_options.values())
        else:
            self.action.options = [
                self.action_options["add"],
                ]
        
    async def get_content(self) -> str:
        if not self.value:
            stat_list = [
                _("**No stats have been set yet.**"),
            ]
        else:
            stat_list = [
                stat.get_display()
                for stat in self.value
            ]
        return _(
            "The class's stats are a list of stats that are added to the "
            "user's stats when they have the class.\n"
            "You can add stats by selecting the **Add stats to the list** "
            "option, then selecting the stats you want, and the amount "
            "to add. *Note that the amount can be negative, and that "
            "the points are added to the maximum of the stat.*\n"
            "%(stat_list)s",
            stat_list="\n".join(stat_list),
        )

    @ui.select(
        placeholder="what do you want to do?",
        options=[],
    )
    async def action(self, interaction: Interaction, _) -> None:
        try:
            action = self.action.values[0]
            actions_views = {
                "add": {
                    "view": StatViewAdd,
                    "func": "add_stat",
                },
                "remove": {
                    "view": StatViewRemove,
                    "func": "remove_stat",
                },
            }

            data = actions_views[action]

            view = data["view"](self)

            func = getattr(view, data["func"])
            await func(interaction)
        except Exception:
            print(traceback.format_exc())
    
    @ui.button(
        label="finish",
        style=ButtonStyle.green
    )
    async def finish(self, interaction: Interaction, _) -> None:
        return await self.on_submit(interaction, edit_message=True)
    
    async def refresh(self, interaction: Interaction) -> None:
        self.check_action_options()

        content = await self.get_content()
        await interaction.response.edit_message(
            content=content,
            view=self,
        )

class _BaseStatView(BaseView):
    def __init__(
        self, 
        base_view: StatView,
    ) -> None:
        super().__init__(timeout=None)
        self.base_view = base_view

        self.user = self.base_view.user
    
    async def get_content(self) -> str:
        return await self.base_view.get_content()

    async def refresh(self, interaction: Interaction) -> None:
        content = await self.get_content()
        await interaction.response.edit_message(
            content=content,
            view=self,
        )
    
    async def button_cancel_callback(self, interaction: Interaction) -> None:
        self.stop()

        await self.base_view.refresh(interaction)
    
    async def on_error(self, interaction: Interaction, error: Exception, item: Item[Any]) -> None:
        print(traceback.format_exc())

class AmountModal(ui.Modal):
    """
    The default modal for any field.
    """
    def __init__(
        self,
    ) -> None:
        super().__init__(title=_("Reward amount"), timeout=None)

        self.amount = ui.TextInput(
            label=_("Minimum amount"),
            placeholder=_("Minimum amount, can be negative."),
            style=TextStyle.short,
            required=True,
        )

        self.add_item(self.amount)
    
    async def raise_error(self, error: ValidationException, interaction: Interaction) -> Literal[False]:
        await interaction.response.send_message(
            str(error)
        )
        return False
    
    async def validate(self, interaction: Interaction) -> bool:
        """|coro|

        Validate the modal.

        """
        amount = self.amount.value.replace(",", ".")


        try:
            await is_number(amount)
        except ValidationException as e:
            return await self.raise_error(e, interaction)

        return True
        

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        print(traceback.format_exc())

    async def on_submit(self, interaction: Interaction) -> None:
        """|coro|

        Called when the user submit the modal.

        """
        is_valid = await self.validate(interaction)

        if not is_valid:
            self.value = None
            self.stop()
            return
        
        amount = self.amount.value.replace(",", ".")
        
        amount = int(amount)

        self.value = amount
        
        await interaction.response.send_message(
            _(
                "Amount set to **%(amount)s**.",
                amount=amount
            ),
            ephemeral=True,
        )
        
        self.stop()


class StatViewAdd(_BaseStatView):
    def __init__(
        self, 
        base_view: StatView,
        ):
        super().__init__(base_view=base_view)
        
        self.stat_list = self.base_view.stat_list

        self.stats: List[AbstractClassStat] = None

        self.items = {
            "selects_stat": [],
            "button_amount": ui.Button(
                emoji="🔢",
                label=_("Amount"),
                style=ButtonStyle.blurple,
                disabled=True,
                row=4
            ),
            "button_confirm": ui.Button(
                emoji="✅",
                label=_("Confirm"),
                style=ButtonStyle.green,
                disabled=True,
                row=4,
            ),
            "button_cancel": ui.Button(
                emoji="❌",
                label=_("Cancel"),
                style=ButtonStyle.red,
                row=4,
            ),
        }

        self.items["button_amount"].callback = self.button_amount_callback
        self.items["button_confirm"].callback = self.button_confirm_callback
        self.items["button_cancel"].callback = self.button_cancel_callback
        
        self.choices = [
            Choice(
                label=stat.name,
                emoji=stat.emoji,
                value=stat,
            ) for stat in self.stat_list
        ]

        self.choices_map = {
            choice.discord_value: choice.value for choice in self.choices
        }

        self.add_item(self.items["select_type"])

        self.add_item(self.items["button_confirm"])

        self.add_item(self.items["button_cancel"])

        choices_list = self.choices
        choices_list = split_list(choices_list, 25)

        if len(choices_list) > 4:
            return #todo choices_list too long
        

        selects_stat = [
            ui.Select(
                placeholder=_("Pick stats in the lists."),
                options=[
                    c.to_select_option() for c in choices
                ],
                max_values=len(choices),
                row=i+1,
            ) for i, choices in enumerate(choices_list)
        ]
        self.items["selects_stat"] = selects_stat

        for select_stat in selects_stat:
            select_stat.callback = self.select_stat_callback
            self.add_item(select_stat)


    async def get_content(self) -> str:
        content = await super().get_content()

        if self.stats:
            content += "\n".join("➕ "+stat.get_display() for stat in self.stats)
        
        return content

    async def add_stat(self, interaction: Interaction) -> None:
        if not self.choices:
            await interaction.response.send_message(
                content=_("There are no stat to add."),
                ephemeral=True
            )
            return

        await self.refresh(interaction)

    async def select_stat_callback(self, interaction: Interaction) -> None:
        self.items["button_confirm"].disabled = True
        self.items["button_amount"].disabled = True

        raw_values = []
        for select in self.items["selects_stat"]:
            raw_values.extend(select.values)


        stats = [self.choices_map[raw_value] for raw_value in raw_values]

        if self.stats:
            amount = self.stats[0].value
        else:
            amount = None

        self.stats = [
            AbstractClassStat(stat=stat, value=amount) for stat in stats
        ]

        if self.stats:
            self.items["button_amount"].disabled = False
            if amount:
                self.items["button_confirm"].disabled = False

        for select in self.items["selects_stat"]:
            for option in select.options:
                if option.value in raw_values:
                    option.default = True
                else:
                    option.default = False

        await self.refresh(interaction)

    async def button_amount_callback(self, interaction: Interaction) -> None:
        modal = AmountModal()

        await interaction.response.send_modal(
            modal,
        )
        await modal.wait()

        if modal.value is not None:
            for stat in self.stats:
                stat.value = modal.value
            
            self.items["button_confirm"].disabled = False

        else:
            self.items["button_confirm"].disabled = True

        await interaction.edit_original_response(
            view=self,
            content=await self.get_content()
        )

    async def button_confirm_callback(self, interaction: Interaction) -> None:
        if self.base_view.field.value:
            self.base_view.field.value.extend(self.stats)
        else:
            self.base_view.field.value = self.stats

        self.stop()

        await self.base_view.refresh(interaction)

class StatViewRemove(_BaseStatView):
    def __init__(
        self, 
        base_view: StatView,
    ) -> None:
        super().__init__(base_view=base_view)

        self.items = {
            "selects_stat": [],
            "button_confirm": ui.Button(
                emoji="✅",
                label=_("Confirm"),
                style=ButtonStyle.green,
                row=4
            ),
            "button_cancel": ui.Button(
                emoji="❌",
                label=_("Cancel"),
                style=ButtonStyle.red,
                row=4
            ),
        }

        self.items["button_confirm"].callback = self.button_confirm_callback
        self.items["button_cancel"].callback = self.button_cancel_callback

        self.add_item(self.items["button_confirm"])
        self.add_item(self.items["button_cancel"])

        self.stats_to_remove: List[AbstractClassStat] = []
        self.stats: List[AbstractClassStat] = self.base_view.value

        self.choices: List[Choice] = []
        self.choices_map: Dict[str, AbstractClassStat] = {}

    async def get_content(self) -> str:
        content = [_("Select the stats you want to remove in the list below.\n\n")]

        for stat in self.stats:
            stat_display = stat.get_display()

            if stat in self.stats_to_remove:
                content.append("➖ " + stat_display)
            else:
                content.append(stat_display)
        
        return "\n".join(content)

    async def remove_stat(self, interaction: Interaction) -> None:

        self.choices = [
            Choice(
                label=stat.get_display(),
                emoji=stat.stat.emoji,
                value=stat,
            ) for stat in self.stats
        ]

        self.choices_map = {
            c.discord_value:c.value for c in self.choices
        }

        choice_lists = split_list(self.choices, 25)

        if len(choice_lists) > 4:
            return #todo choices_list too long

        selects_stat = [
            ui.Select(
                placeholder=_("Select stats to remove in the list"),
                options=[c.to_select_option() for c in choices],
                row=i,
                max_values=len(choices),
            ) for i, choices in enumerate(choice_lists)
        ]
        for select in selects_stat:
            select.callback = self.select_stat_callback
            self.add_item(select)
        
        self.items["selects_stat"] = selects_stat

        await self.refresh(interaction)
    
    async def select_stat_callback(self, interaction: Interaction) -> None:

        raw_values = []
        for select in self.items["selects_stat"]:
            raw_values.extend(select.values)
        
        values = [self.choices_map[v] for v in raw_values]

        self.stats_to_remove = values

        for select in self.items["selects_stat"]:
            for option in select.options:
                if option.value in raw_values:
                    option.default = True
                else:
                    option.default = False

        await self.refresh(interaction)
        
    async def button_confirm_callback(self, interaction: Interaction) -> None:
        self.base_view.field.value = [
            stat for stat in self.stats if stat not in self.stats_to_remove
        ]
        self.stop()

        await self.base_view.refresh(interaction)
    
class Stat(Field):
    def __init__(
        self, 
        name: str, 
        label: str, 
        required: bool = False, 
        validators: List[Callable[[str], bool]] = [], 
        appear_validators: List[Callable[[str], bool]] = [], 
        set_validators: List[Callable[[str], bool]] = [],
        default: Optional[List[AbstractClassStat]] = None, 
        **kwargs) -> None:
        super().__init__(
            name, 
            label, 
            required, 
            validators, 
            appear_validators, 
            set_validators,
            default, 
            **kwargs
        )
        self.value = default or []

        self.stat_list: AccessibleList
    
    async def get_stat_list(self, interaction: Interaction) -> None:
        cluster = await self.get_cluster(interaction)

        stats = await cluster.stats.all()

        self.stat_list = stats
        
    async def ask(self, interaction: Interaction) -> Optional[bool]:
        if not hasattr(self, "stat_list"):
            await self.get_stat_list(interaction)
        
        if not self.stat_list and not self.default:
            await interaction.response.send_message(
                content=_("There are no stats configured, so you can't add stats."),
                ephemeral=True
            )
            return
        
        view = StatView(
            field=self,
        )
        
        content = await view.get_content()
        await interaction.response.send_message(
            content=content,
            embed=None,
            view=view,
            ephemeral=True,
        )
        await view.wait()
        
    
    async def display(self) -> str:
        if not self.value:
            self.display_value = _("*Unanswered*")
        else:
            self.display_value = "\n".join([
                await stat.get_display() 
                for stat in self.value
            ])

            if len(self.display_value) > 1048:
                self.display_value = self.display_value[:1045] + "..."

        return self.display_value
    