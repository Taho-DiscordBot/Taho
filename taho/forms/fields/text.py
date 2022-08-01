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
from discord.ui import Modal, TextInput
from taho.babel import _
from .field import Field, FieldModal

if TYPE_CHECKING:
    from typing import Optional, List, Callable, TypeVar


class TextModal(FieldModal):
    def __init__(
        self,
        field: Field,
        *, title: str, 
        label: str, 
        default: Optional[str] = None,
        max_length: Optional[int] = None, 
        min_length: Optional[int] = None,
    ) -> None:
        super().__init__(field=field, title=title, default=default)

        self.field = field

        self.answer = TextInput(
                label=label,
                placeholder=_("Enter a value"),
                style=TextStyle.short if max_length and max_length < 50 else TextStyle.long,
                max_length=max_length,
                min_length=min_length,
                required=True,
                default=self.default
            )

        self.add_item(self.answer)

        self.value: str = None
    
    async def on_submit(self, interaction: Interaction) -> None:

        value = self.answer.value

        self.field.value = value
        self.field.default = value


        await super().on_submit(interaction)
    

class Text(Field):
    def __init__(
        self, 
        name: str, 
        label: str, 
        required: bool = False,
        validators: List[Callable[[str], bool]] = [], 
        appear_validators: List[Callable[[str], bool]] = [], 
        default: Optional[str] = None,
        max_length: Optional[int] = None,
        min_length: Optional[int] = 3,
        **kwargs
    ) -> None:
        super().__init__(
            name, 
            label, 
            required, 
            validators, 
            appear_validators, 
            default,
            **kwargs)
        
        self.max_length = max_length
        self.min_length = min_length
    
    async def ask(self, interaction: Interaction) -> Optional[bool]:
        modal = TextModal(
                field=self,
                title=_("Enter a value"),
                label=self.label,
                max_length=self.max_length,
                min_length=self.min_length,
                default=self.default
            )
        await interaction.response.send_modal(
            modal
        )
        await modal.wait()

        await self.display()
        
    
    async def display(self) -> str:
        if self.value is None:
            self.display_value = _("*Unanswered*")
        else:
            self.display_value = self.value
        
        return self.display_value
