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
from discord import Interaction, SelectOption
from discord.ui import Select as _Select
from taho.babel import lazy_gettext
from .field import Field, FieldModal
from enum import Enum

if TYPE_CHECKING:
    from typing import Optional, List, Callable, TypeVar

    T = TypeVar("T")

class SelectModal(FieldModal):
    def __init__(
        self,
        field: Field,
        *, title: str, 
        choices: List[Choice] = [],
        min_values: Optional[int] = 1, 
        max_values: Optional[int] = 1,
    ) -> None:
        super().__init__(field=field, title=title)

        self.field = field
        self.min_values = min_values
        self.max_values = max_values

        self.response_map = {
            c.discord_value: c.value for c in choices
        }

        self.answer = _Select(
                placeholder=lazy_gettext("Select a value"),
                min_values=min_values,
                max_values=max_values,
                options=[SelectOption(
                        label=c.label,
                        value=c.discord_value,
                    ) for c in choices
                ]
            )

        self.add_item(self.answer)

        self.value: str = None
    
    async def on_submit(self, interaction: Interaction) -> None:
        self.field.value = [
            self.response_map[a] for a in self.answer.values
        ]
        if self.min_values == 1 and self.max_values == 1:
            self.field.value = self.field.value[0]
        
        await super().on_submit(interaction)
    
class Choice:
    def __init__(
        self, 
        label: str, 
        value: T, 
    ) -> None:
        self.label = label
        self.value = value

        self.discord_value = self._get_discord_value()
    
    def _get_discord_value(self) -> str:
        if isinstance(self.value, Enum):
            return str(self.value.value)
        
        return str(self.value)


class Select(Field):
    def __init__(
        self, 
        name: str, 
        label: str, 
        required: bool = False,
        validators: List[Callable[[str], bool]] = [], 
        appear_validators: List[Callable[[str], bool]] = [], 
        current: bool = False,
        choices: List[Choice] = [],
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
            current, 
            **kwargs)
        
        self.choices = choices
        self.min_values = min_values
        self.max_values = max_values
        
    
    async def ask(self, interaction: Interaction) -> None:
        modal = SelectModal(
                field=self,
                title=lazy_gettext("Enter a value"),
                choices=self.choices,
                min_values=self.min_values,
                max_values=self.max_values
            )
        await interaction.response.send_modal(
            modal
        )
        await modal.wait()

    
    async def display(self) -> str:
        if self.value is None:
            self.display_value = lazy_gettext("*Unanswered*")
        else:
            response_map = {
                c.value: c.label for c in self.choices
            }

            if self.min_values == 1 and self.max_values == 1:
                self.display_value = response_map[self.value]
            else:
                self.display_value = ", ".join(
                    response_map[v] for v in self.value
                )
        return self.display_value