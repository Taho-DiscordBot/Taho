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
from discord import Interaction, TextStyle
from discord.ui import TextInput
from taho.babel import _
from taho.forms.validators import is_number
from .field import Field, FieldModal

if TYPE_CHECKING:
    from typing import Union, List, Callable


class NumberModal(FieldModal):
    def __init__(
        self,
        field: Field,
        *, title: str, 
        label: str, 
        required: bool = True,
    ) -> None:
        super().__init__(field=field, title=title)

        self.answer = TextInput(
                label=label,
                placeholder=_("Enter a value"),
                style=TextStyle.short,
                min_length=1,
                required=required,
            )

        self.add_item(self.answer)

        self.value: Union[int, float] = None
    
    async def on_submit(self, interaction: Interaction) -> None:
        self.field.value = self.answer.value.replace(",", ".")

        old_validators = self.field.validators
        self.field.validators = [
            lambda x: is_number(x),
        ]

        is_valid = await self.field.validate(interaction)

        await self.field.display()

        if not is_valid:
            self.stop()
            return

        self.field.validators = old_validators

        try:
            self.field.value = int(self.field.value)
        except ValueError:
            self.field.value = float(self.field.value)
        
        await super().on_submit(interaction)
    

class Number(Field):
    def __init__(
        self, 
        name: str, 
        label: str, 
        required: bool = False,
        validators: List[Callable[[str], bool]] = [], 
        appear_validators: List[Callable[[str], bool]] = [], 
        current: bool = False,
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
        
    
    async def ask(self, interaction: Interaction) -> None:
        modal = NumberModal(
                field=self,
                title=_("Enter a value"),
                label=self.label,
                required=self.required,
            )
        await interaction.response.send_modal(
            modal
        )
        await modal.wait()

        await self.display()
        
    
    async def display(self) -> str:
        if self.value is None:
            self.display_value = _("*Unanswered*")
        elif self.value == -1:
            self.display_value = _("Infinite")
        else:
            self.display_value = str(self.value)
        
        return self.display_value
