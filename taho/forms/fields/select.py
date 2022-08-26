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
from discord import ButtonStyle, Interaction
from discord.ui import Select as _Select, Button
from taho.babel import _
from .field import Field, FieldView
from ..validators import min_length, max_length
from taho.utils import split_list, _get_display

if TYPE_CHECKING:
    from typing import Optional, List, Callable, TypeVar
    from ..choice import Choice

    T = TypeVar("T")

__all__ = (
    "SelectView",
    "Select"
)

class SelectView(FieldView):
    def __init__(
        self,
        field: Field,
        *,
        choices: List[Choice] = [],
        min_values: Optional[int] = 1, 
        max_values: Optional[int] = 1,
        default: Optional[List[T]] = None,
    ) -> None:
        super().__init__(field=field, default=default)

        self.choices = choices
        self.min_values = min_values
        self.max_values = max_values

        if self.default is not None:
            for c in self.choices:
                if c.value in self.default:
                    c.selected = True

        self.response_map = {
            c.discord_value: c.value for c in choices
        }

        if len(self.choices) > 100:
            raise ValueError("Too many choices")
        
        choices_lists = split_list(self.choices, 25)
        self.answers: List[_Select] = []

        for i, choices_list in enumerate(choices_lists):
            select = _Select(
                    placeholder=_("Select a value"),
                    min_values=self.min_values,
                    max_values=self.max_values,
                    options=[
                        c.to_select_option() for c in choices_list
                    ],
                    row=i,
                )
            self.answers.append(select)
            self.add_item(select)
        
        if len(self.answers) == 1:
            self.answers[0].callback = self.on_submit
        else:
        
            submit_button = Button(
                style=ButtonStyle.green,
                label=_("Submit"),
                row=i+1
            )
            submit_button.callback = self.on_submit
            self.add_item(submit_button)

        self.value: str = None
    
    async def on_submit(self, interaction: Interaction) -> None:
        values = []
        for answer in self.answers:
            values.extend(answer.values)

        self.field.value = [
            self.response_map[v] for v in values
        ]

        self.field.default = self.field.value

        is_valid = await self.field._validate(
            self.field.value,
            lambda x: min_length(x, self.min_values),
            lambda x: max_length(x, self.max_values),
        )

        if not is_valid:
            self.stop()
            return

        if self.min_values == 1 and self.max_values == 1:
            self.field.value = self.field.value[0]
        
        await super().on_submit(interaction, edit_message=True)

class Select(Field):
    def __init__(
        self, 
        name: str, 
        label: str, 
        description: str = None,
        required: bool = False,
        validators: List[Callable[[str], bool]] = [], 
        appear_validators: List[Callable[[str], bool]] = [], 
        set_validators: List[Callable[[str], bool]] = [],
        default: Optional[T] = None,
        choices: List[Choice] = None,
        min_values : Optional[int] = 1,
        max_values: Optional[int] = 1,
        **kwargs
    ) -> None:
        super().__init__(
            name, 
            label, 
            required, 
            validators, 
            appear_validators, 
            set_validators,
            default,
            **kwargs)
        
        self.description = description

        self.choices = choices
        self.min_values = min_values
        self.max_values = max_values

        if self.max_values == -1 and self.choices:
            self.max_values = len(self.choices)

        if not self.description:
            self.description = _(
                "Select between %(min_values)s and %(max_values)s values.",
                min_values=min_values,
                max_values=max_values,
            )
        
    async def get_choices(self, interaction: Interaction = None) -> bool:
        if interaction:
            await interaction.response.send_message(
                _("No choices available.")
            )
        return False

    async def ask(self, interaction: Interaction) -> Optional[bool]:
        if not self.choices:
            is_valid = await self.get_choices(interaction)
            if not is_valid:
                return
        
        view = SelectView(
                field=self,
                choices=self.choices,
                min_values=self.min_values,
                max_values=self.max_values,
                default=self.default
            )
        await interaction.response.send_message(
            content=self.description,
            embed=None,
            view=view,
            ephemeral=True,
        )
        await view.wait()

    async def display(self) -> str:
        if self.value is None:
            self.display_value = _("*Unanswered*")
        else:
            if not self.choices:
                await self.get_choices()
            
            if not self.choices:
                await self.set_value(None)
            else:
                if isinstance(self.value, list):
                    self.display_value = ", ".join(
                        [_get_display(v) for v in self.value]
                    )
                else:
                    self.display_value = _get_display(self.value)

        return self.display_value