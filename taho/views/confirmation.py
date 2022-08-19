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
from discord import ui, ButtonStyle
from taho.babel import _

if TYPE_CHECKING:
    from discord import Interaction

__all__ = (
    "ConfirmationView",
)

class ConfirmationView(ui.View):
    def __init__(self):
        super().__init__()

        self.value: bool = False

        self.confirm = ui.Button(
            label=_("Confirm"),
            emoji="✅",
            style=ButtonStyle.green
        )
        self.confirm.callback = self.confirm_callback
        self.add_item(self.confirm)

        self.cancel = ui.Button(
            label=_("Cancel"),
            emoji="❌",
            style=ButtonStyle.red
        )
        self.cancel.callback = self.cancel_callback
        self.add_item(self.cancel)
    
    async def confirm_callback(self, interaction: Interaction):
        self.value = True
        
        await interaction.response.defer()
        self.stop()
    
    async def cancel_callback(self, interaction: Interaction):
        self.value = False
        
        try:
            await interaction.response.edit_message(
                _("Cancelled.")
            )
        except:
            await interaction.response.send_message(
                _("Cancelled."),
                ephemeral=True
            )
        self.stop()

