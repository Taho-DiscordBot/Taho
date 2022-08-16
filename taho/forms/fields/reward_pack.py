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
from taho.utils.abstract import AbstractReward
from taho.enums import ItemType, RegenerationType
from taho.database.models import Item
from taho.exceptions import ValidationException
from .field import Field, FieldView
from ..choice import Choice
from ..validators import is_number

if TYPE_CHECKING:
    from typing import Union, List, Callable, Optional, Dict, Any, Literal
    from taho.utils.abstract import AbstractRewardPack

    from taho.emoji import Emoji
    from taho.database.models import Role, Stat

__all__ = (
    "RewardPack",
)

class RewardPackView(FieldView):
    def __init__(
        self, 
        field: RewardPack, 
        default: AbstractRewardPack,
        ) -> None:
        super().__init__(field, default)
        self.field: RewardPack

        self.rewardable_list = self.field.rewardable_list

        self.action.placeholder = _("What do you want to do?")
        self.action_options = {
            "add": SelectOption(
                label=_("Add a reward"),
                value="add",
            ),
            "remove": SelectOption(
                label=_("Remove a reward"),
                value="remove",
            ),
            "delete": SelectOption(
                label=_("Delete the pack"),
                value="delete",
            )
        }

        self.finish.label = _("Finish")

        self.check_action_options()
    
    def check_action_options(self) -> None:

        if self.field.pack.rewards:
            self.action.options = list(self.action_options.values())
        else:
            self.action.options = [
                self.action_options["add"],
                self.action_options["delete"]
                ]
        
    async def get_content(self) -> str:
        return await self.field.display()

    @ui.select(
        placeholder="what do you want to do?",
        options=[],
    )
    async def action(self, interaction: Interaction, _) -> None:
        try:
            action = self.action.values[0]
            actions_views = {
                "add": {
                    "view": RewardPackViewAdd,
                    "func": "add_reward",
                },
                "remove": {
                    "view": RewardPackViewRemove,
                    "func": "remove_reward",
                },
                "delete": {
                    "view": RewardPackViewDelete,
                    "func": "delete_pack",
                }
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

class AmountModal(ui.Modal):
    """
    The default modal for any field.
    """
    def __init__(
        self,
    ) -> None:
        super().__init__(title=_("Reward amount"))

        self.min_amount = ui.TextInput(
            label=_("Minimum amount"),
            placeholder=_("Minimum amount, can be negative."),
            style=TextStyle.short,
            required=True,
        )

        self.max_amount = ui.TextInput(
            label=_("Maximum amount"),
            placeholder=_("Maximum amount, can be negative. Keep empty for fix amount."),
            style=TextStyle.short,
            required=False,
        )
        self.add_item(self.min_amount)
        self.add_item(self.max_amount)
    
    async def raise_error(self, error: ValidationException, interaction: Interaction) -> Literal[False]:
        await interaction.response.send_message(
            str(error)
        )
        return False
    
    async def validate(self, interaction: Interaction) -> bool:
        """|coro|

        Validate the modal.

        """
        min_amount = self.min_amount.value.replace(",", ".")
        max_amount = self.max_amount.value.replace(",", ".") if self.max_amount.value else None


        try:
            await is_number(min_amount)
        except ValidationException as e:
            return await self.raise_error(e, interaction)

        if max_amount:
            try:
                await is_number(max_amount)
            except ValidationException as e:
                return await self.raise_error(e, interaction)
        
        if max_amount and min_amount > max_amount:
            error = ValidationException(
                _("Minimum amount can't be greater than maximum amount.")
            )
            return await self.raise_error(error, interaction)
        
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
        
        min_amount = self.min_amount.value.replace(",", ".")
        max_amount = self.max_amount.value.replace(",", ".") if self.max_amount.value else None
        
        min_amount = float(min_amount)
        max_amount = float(max_amount) if max_amount else None
        
        self.value = min_amount, max_amount
        if max_amount:
            await interaction.response.send_message(
                _(
                    "Reward amount set to %(min_amount)s/%(max_amount)s.",
                    min_amount=min_amount,
                    max_amount=max_amount,
                    ),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                _(
                    "Reward amount set to %(amount)s.",
                    amount=min_amount,
                    ),
                ephemeral=True,
            )
        
        self.stop()

class _BaseRewardPackView(ui.View):
    def __init__(
        self, 
        base_view: RewardPackView,
    ) -> None:
        super().__init__()
        self.base_view = base_view
    
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

class RewardPackViewAdd(_BaseRewardPackView):
    def __init__(
        self, 
        base_view: RewardPackView,
        ):
        super().__init__(base_view=base_view)
        
        self.rewardable_list = self.base_view.rewardable_list

        self.rewards: List[AbstractReward] = None
        self.type: Literal["item", "role", "stat"] = None

        texts = {
            "item": _("Item (or currency)"),
            "role": _("RP Role"),
            "stat": _("Stat"),
        }
        self.items = {
            "select_type": ui.Select(
            placeholder=_("What type of reward do you want to add?"),
            options=[
                SelectOption(
                    label=text,
                    value=value,
                ) for value, text in texts.items() if self.rewardable_list[value]
            ],
            row=0
            ),
            "selects_stuff": [],
            "select_extra": ui.Select(
                placeholder=_("What to you want to add?"),
                options=[],
                row=3,
            ),
            "modal_amount": ui.Button(
                emoji="🔢",
                label=_("Define quantity"),
                style=ButtonStyle.blurple,
                row=4,
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
        del texts
    
        self.select_extra_options = {
            "item": [
                SelectOption(
                    label=_("Quantity"),
                    value="quantity",
                ),
                SelectOption(
                    label=_("Durability"),
                    value="durability",
                ),
            ],
            "stat": [
                SelectOption(
                    label=_("Maximum"),
                    value="maximum",
                ),
                SelectOption(
                    label=_("Regeneration"),
                    value="regeneration",
                ),
            ],
            "role": []
        }

        self.items["select_type"].callback = self.select_type_callback
        self.items["select_extra"].callback = self.select_extra_callback
        self.items["modal_amount"].callback = self.modal_amount_callback
        self.items["button_confirm"].callback = self.button_confirm_callback
        self.items["button_cancel"].callback = self.button_cancel_callback

        self.choices_map = {
            item: [
                Choice(
                    label=value["name"],
                    value=value[item],
                    emoji=value["emoji"]
                ) for value in values
            ] for item, values in self.rewardable_list.items()
        }

        self.add_item(self.items["select_type"])

        self.add_item(self.items["button_confirm"])

        self.add_item(self.items["button_cancel"])

    async def add_reward(self, interaction: Interaction) -> None:
        if all(value == [] for value in self.rewardable_list.values()):
            await interaction.response.send_message(
                content=_("There are no rewards available to add (role, item or stat)."),
                ephemeral=True
            )
            return

        await self.refresh(interaction)

    async def select_type_callback(self, interaction: Interaction) -> None:
        self.items["button_confirm"].disabled = True
        self.remove_item(self.items["modal_amount"])
        self.remove_item(self.items["select_extra"])

        for item in self.items["selects_stuff"]:
            self.remove_item(item)


        self.type = self.items["select_type"].values[0]

        for option in self.items["select_type"].options:
            if option.value == self.type:
                option.default = True
            else:
                option.default = False

        choices_list = self.choices_map[self.type]
        choices_list = split_list(choices_list, 25)

        if len(choices_list) > 2:
            return #todo here
        
        select_stuff_texts = {
            "item": _("Pick an item in the list."),
            "role": _("Pick a role in the list."),
            "stat": _("Pick a stat in the list."),
        }

        selects_stuff = [
            ui.Select(
                placeholder=select_stuff_texts[self.type],
                options=[
                    c.to_select_option() for c in choices
                ],
                max_values=len(choices),
                row=i+1,
            ) for i, choices in enumerate(choices_list)
        ]
        self.items["selects_stuff"] = selects_stuff

        for select_stuff in selects_stuff:
            select_stuff.callback = self.select_stuff_callback
            self.add_item(select_stuff)
        
        await self.refresh(interaction)
        
    async def select_stuff_callback(self, interaction: Interaction) -> None:
        self.items["button_confirm"].disabled = True
        self.remove_item(self.items["modal_amount"])
        self.remove_item(self.items["select_extra"])

        raw_values = []
        for select in self.items["selects_stuff"]:
            raw_values.extend(select.values)

        values_map = {
            c.discord_value:c.value for c in self.choices_map[self.type]
        }

        values = [values_map[raw_value] for raw_value in raw_values]

        self.rewards = [
            AbstractReward(stuff=value) for value in values
        ]

        self.items["select_extra"].options = self.select_extra_options[self.type]

        if self.type == "role":
            self.items["button_confirm"].disabled = False
        
        elif self.type == "item":
            if all(value.type in (ItemType.resource, ItemType.currency) \
                or value.durability == -1 for value in values):

                self.items["select_extra"].disabled = True
                self.items["select_extra"].options[0].default = True

            self.add_item(self.items["select_extra"])

            self.add_item(self.items["modal_amount"])
        
        elif self.type == "stat":

            if all(value.regeneration == RegenerationType.no_regen \
                for value in values):
                self.items["select_extra"].disabled = True
                self.items["select_extra"].options[0].default = True

            else:
                self.items["select_extra"].callback = self.add_reward_extra
            
            self.add_item(self.items["select_extra"])

            self.add_item(self.items["modal_amount"])

        for select in self.items["selects_stuff"]:
            for option in select.options:
                if option.value in raw_values:
                    option.default = True
                else:
                    option.default = False

        await self.refresh(interaction)

    async def button_confirm_callback(self, interaction: Interaction) -> None:
        self.base_view.field.pack.add_rewards(*self.rewards)

        self.stop()

        await self.base_view.refresh(interaction)

    async def select_extra_callback(self, interaction: Interaction) -> None:
        extra = self.items["select_extra"].values[0]

        if extra == "durability":
            for reward in self.rewards:
                if reward.stuff.type == ItemType.consumable and \
                    reward.stuff.durability != -1:
                        reward.durability = True
        
        elif extra == "regeneration":
            for reward in self.rewards:
                if reward.stuff.regeneration != RegenerationType.no_regen:
                        reward.regeneration = True
        
        if self.rewards[0].min_amount is not None:
            self.items["button_confirm"].disabled = False
        
        for option in self.items["select_extra"].options:
            if option.value == extra:
                option.default = True
            else:
                option.default = False
        
        await self.refresh(interaction)
        
    async def modal_amount_callback(self, interaction: Interaction) -> None:
        modal = AmountModal()

        await interaction.response.send_modal(
            modal,
        )
        await modal.wait()

        if modal.value is not None:
            for reward in self.rewards:
                if not (isinstance(reward.stuff, Item) and reward.stuff.type == ItemType.currency):
                    reward.min_amount = int(modal.value[0])
                    reward.max_amount = int(modal.value[1]) if modal.value[1] else None

            self.items["button_confirm"].disabled = False

        else:
            self.items["button_confirm"].disabled = True

        await interaction.edit_original_response(
            view=self,
        )
        
class RewardPackViewRemove(_BaseRewardPackView):
    def __init__(
        self, 
        base_view: RewardPackView,
    ) -> None:
        super().__init__(base_view=base_view)

        self.guild_id = self.base_view.field.form.guild.id
        
        self.items = {
            "selects_stuff": [],
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

        self.rewards_to_remove: List[AbstractReward] = []
        self.rewards: List[AbstractReward] = self.base_view.field.pack.rewards

        self.choices: List[Choice] = []
        self.choices_map: Dict[str, AbstractReward] = []

    async def get_content(self) -> str:
        content = [_("Select the rewards you want to remove in the list below.\n\n")]

        for reward in self.rewards:
            reward_display = await reward.get_display(guild_id=self.guild_id)

            if reward in self.rewards_to_remove:
                content.append("➖ " + reward_display)
            else:
                content.append(reward_display)
        
        return "\n".join(content)

    async def remove_reward(self, interaction: Interaction) -> None:

        self.choices = [
            Choice(
                label=await reward.get_display(guild_id=self.guild_id),
                value=reward
            ) for reward in self.rewards
        ]

        self.choices_map = {
            c.discord_value:c.value for c in self.choices
        }

        choice_lists = split_list(self.choices, 25)

        if len(choice_lists) > 4:
            return #todo here

        selects_stuff = [
            ui.Select(
                placeholder=_("Select rewards to remove in the list"),
                options=[c.to_select_option() for c in choices],
                row=i,
                max_values=len(choices),
            ) for i, choices in enumerate(choice_lists)
        ]
        for select in selects_stuff:
            select.callback = self.select_stuff_callback
            self.add_item(select)
        
        self.items["selects_stuff"] = selects_stuff

        await self.refresh(interaction)
    
    async def select_stuff_callback(self, interaction: Interaction) -> None:

        values = []
        for select in self.items["selects_stuff"]:
            values.extend(select.values)
        
        values = [self.choices_map[v] for v in values]

        self.rewards_to_remove = values

        await self.refresh(interaction)
        
    async def button_confirm_callback(self, interaction: Interaction) -> None:
        self.base_view.field.pack.remove_rewards(*self.rewards_to_remove)

        self.stop()

        await self.base_view.refresh(interaction)
    
class RewardPackViewDelete(_BaseRewardPackView):
    def __init__(
        self, 
        base_view: RewardPackView,
        ):
        super().__init__(base_view=base_view)

        self.items = {
            "button_confirm": ui.Button(
                emoji="✅",
                label=_("Confirm"),
                style=ButtonStyle.green,
            ),
            "button_cancel": ui.Button(
                emoji="❌",
                label=_("Cancel"),
                style=ButtonStyle.red,
            ),
        }

        self.items["button_confirm"].callback = self.button_confirm_callback
        self.items["button_cancel"].callback = self.button_cancel_callback

        self.add_item(self.items["button_confirm"])
        self.add_item(self.items["button_cancel"])

    async def get_content(self) -> str:
        content = await super().get_content()
        content += "\n\n" + _("__**Are you sure you want to delete this pack?**__")
        return content
    
    async def delete_pack(self, interaction: Interaction) -> None:
        await self.refresh(interaction)

    async def button_confirm_callback(self, interaction: Interaction) -> None:
        self.base_view.field.form.fields.remove(self.base_view.field)

        self.base_view.field.form.fields[0].is_current = True

        await interaction.response.edit_message(
            content=_("The pack has been deleted."),
            view=None
        )
        self.stop()

        self.base_view.stop()
    
class RewardPack(Field):
    def __init__(
        self, 
        pack: Optional[AbstractRewardPack],
        validators: List[Callable[[str], bool]] = [],
        rewardable_list: Dict[str, List[Dict[str, Union[str, Emoji, Item, Role, Stat, None]]]] = {},
        **kwargs
    ) -> None:
        name = label = pack.get_name()
        self.pack = pack
        self.rewardable_list = rewardable_list
        super().__init__(
            name,
            label,
            validators=validators, 
            default=pack,
            **kwargs)
        
    async def ask(self, interaction: Interaction) -> Optional[bool]:
        view = RewardPackView(self, self.pack)
        content = await view.get_content()

        await interaction.response.send_message(
            content=content,
            view=view,
            ephemeral=True
        )
        await view.wait()
        self.value = self.pack
        
    
    async def display(self) -> str:
        if not self.pack.rewards:
            self.display_value = _("*No rewards*")
        else:
            guild_id = self.form.guild.id
            self.display_value = "\n".join([
                await reward.get_display(guild_id=guild_id) for reward in self.pack.rewards
            ])
        
        return self.display_value
    