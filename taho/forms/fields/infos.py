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
from .field import Field
from ..form import Form
from taho.babel import _
from taho.abstract import AbstractInfo

if TYPE_CHECKING:
    from typing import List, Callable, Optional, TypeVar
    from discord import Interaction

    T = TypeVar("T")

__all__ = (
    "Infos",
)

class Infos(Field):
    def __init__(
        self, 
        name: str, 
        label: str, 
        infos_fields: List[Field],
        required: bool = False, 
        validators: List[Callable[[str], bool]] = [], 
        appear_validators: List[Callable[[str], bool]] = [], 
        set_validators: List[Callable[[str], bool]] = [], 
        default: Optional[List[AbstractInfo]] = None,
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
            **kwargs
        )
        self.infos_fields = infos_fields
        
        self._initial_display()

    async def ask(self, interaction: Interaction) -> Optional[bool]:
        if self.default:
            default_map = {
                info.key: info.value for info in self.default
            }
            for field in self.infos_fields:
                if field.name in default_map:
                    field.default = default_map[field.name]

        form = Form(
            self.label,
            fields=self.infos_fields,
            edit_after=False
        )
        await form.send(interaction=interaction, ephemeral=True)
        await form.wait()
        
        interaction = form.final_interaction

        if form.is_canceled():
            await interaction.response.edit_message(
                content=_(
                    "The field **%(field_name)s** has not been updated.",
                    field_name=self.label
                ),
                view=None,
                embed=None
            )
        else:
            value = []
            for field in form.fields:
                if field.value:
                    value.append(
                        AbstractInfo(field.name, field.value)
                    )
            await self.set_value(value)

            await interaction.response.edit_message(
                content=_(
                    "The field **%(field_name)s** has been updated.",
                    field_name=self.label
                ),
                view=None,
                embed=None
            )
    
    def _initial_display(self) -> str:
        display = []
        for field in self.infos_fields:
            if field.required and field.value is None:
                display.append(_(
                "**%(info_name)s:** %(info_value)s",
                info_name=field.label,
                info_value=_("*Unanswered*")
            ))
        if display:
            self.display_value = "\n".join(display)
        else:
            self.display_value = _("*Unanswered*")
        
        return self.display_value

    async def display(self) -> str:
        if not self.value:
            return self._initial_display()
        else:
            display = []
            field_map = {
                field.name: field.label for field in self.infos_fields
            }
            for info in self.value:
                display.append(_(
                    "**%(info_name)s:** %(info_value)s",
                    info_name=field_map[info.key],
                    info_value=str(info.value)
                ))
            self.display_value = "\n".join(display)
        return self.display_value

    def is_completed(self) -> bool:
        return (self.required and all(field.is_completed() for field in self.infos_fields)) \
                or not self.required \
                or not self.must_appear()
    
    async def set_value(self, value: T) -> None:
        self.value = value
        await self.display()
        field_map = {
            field.name: field for field in self.infos_fields
        }
        for v in self.value:
            await field_map[v.key].set_value(v.value)