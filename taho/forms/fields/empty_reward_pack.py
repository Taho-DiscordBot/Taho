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
from discord import Interaction, ui, AllowedMentions, TextStyle, utils as dutils
from taho.babel import _
from .field import Field, FieldModal
from .reward_pack import RewardPack
from ..choice import Choice
from ..validators import *
from taho.enums import get_reward_type_text
from taho.utils.abstract import AbstractRewardPack


if TYPE_CHECKING:
    from typing import List, Callable, Optional, Dict, Union
    from taho.enums import RewardType
    from taho.emoji import Emoji
    from taho.database.models import Item, Role, Stat

__all__ = (
    "EmptyRewardPackModal",
    "EmptyRewardPack",
)

class EmptyRewardPackModal(FieldModal):
    def __init__(
        self, 
        field: EmptyRewardPack,
        reward_types: Optional[List[RewardType]] = None
        ) -> None:
        title=_("Create a reward pack")
        super().__init__(
            field, 
            title=title, 
        )

        self.reward_types = reward_types

        if self.reward_types:
            self.reward_type_choices = []
            for reward_type in self.reward_types:
                choice = Choice(
                    label=get_reward_type_text(reward_type),
                    value=reward_type,
                )
                self.reward_type_choices.append(choice)
            
            self.reward_type_select = ui.Select(
                placeholder=_("Choose when the rewards will be given"),
                options=[c.to_select_option() for c in self.reward_type_choices]

            )
            self.add_item(self.reward_type_select)
        
        self.luck = ui.TextInput(
            label=_("Pack loot chance"),
            placeholder=_("A percentage between 0 and 100. Max two decimals are allowed."),
            style=TextStyle.short,
            max_length=6,
            min_length=1,
            required=True,
            )
        
        self.add_item(self.luck)
    
    async def on_submit(self, interaction: Interaction) -> None:
        validators = []

        value = {
            "luck": self.luck.value.replace(",", "."),
            "reward_type": self.reward_type_select.values if self.reward_types else None,
        }
        self.field.value = value

        if self.reward_types:
            validators.append(
                lambda x: required(
                    x["reward_type"], 
                    _("Reward Type"),
                    absolute=False
                )
            )
        validators += [
            lambda x: is_number(x["luck"]),
            lambda x: min_value(float(x["luck"]), 0),
            lambda x: max_value(float(x["luck"]), 100),
        ]

        is_valid = await self.field._validate(interaction, *validators)

        if not is_valid:
            self.stop()
            return
        
        if self.reward_types:
            choice_map = {c.discord_value: c.value for c in self.reward_type_choices}
            value["reward_type"] = choice_map[value["reward_type"][0]]
        
        value["luck"] = round(float(value["luck"]), 2)

        self.field.value = value

        is_valid = await self.field.validate(interaction)

        pack = AbstractRewardPack(
            type=value["reward_type"],
            luck=value["luck"],
        )

        new_field = RewardPack(
            pack=pack,
            rewardable_list=self.field.rewardable_list,
        )
        new_field.form = self.field.form

        current_field = dutils.find(
            lambda f: f.is_current, self.field.form.fields
        )
        current_field.is_current = False
        
        new_field.is_current = True

        await new_field.display()
        self.field.form.fields = [new_field] + self.field.form.fields

        if is_valid:
            await interaction.response.send_message(
                _(
                    "New reward pack **%(pack_name)s** successfully created.", 
                    pack_name=new_field.label
                ),
                ephemeral=True,
                allowed_mentions=AllowedMentions.none()
            )

        self.stop() 

    async def on_error(self, interaction: Interaction, error: Exception) -> None:
        import traceback
        print(traceback.format_exc())
        return await super().on_error(interaction, error)

class EmptyRewardPack(Field):
    def __init__(
        self,
        validators: List[Callable[[str], bool]] = [],
        reward_types: Optional[List[RewardType]] = None,
        rewardable_list: Dict[str, List[Dict[str, Union[str, Emoji, Item, Role, Stat, None]]]] = {},
        **kwargs
        ) -> None:
        name = "empty_reward_pack"
        label = _("Create a reward pack")
        self.rewardable_list = rewardable_list
        super().__init__(
            name, 
            label, 
            validators=validators,
            **kwargs)
        
        self.display_value = _("Click on **Respond** to create a new reward pack")
        self.reward_types = reward_types
    
    async def ask(self, interaction: Interaction) -> Optional[bool]:
        modal = EmptyRewardPackModal(
            field=self,
            reward_types=self.reward_types
            )
        await interaction.response.send_modal(
            modal
        )
        await modal.wait()

    
    async def display(self) -> str:
        return self.display_value
