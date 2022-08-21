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
from discord import ui
from taho.babel import _

if TYPE_CHECKING:
    from discord.abc import Snowflake
    from discord import Interaction, Message
    from typing import Optional

__all__ = (
    "BaseView",
)

class BaseView(ui.View):
    def __init__(
        self, 
        user: Optional[Snowflake] = None,
        *args,
        **kwargs
        ):
        self.user = user
        self.msg: Optional[Message] = None
        super().__init__(*args, **kwargs)
    
    async def interaction_check(self, interaction: Interaction) -> bool:
        if not self.user:
            return True
        allow = self.user.id == interaction.user.id

        if not allow:
            await interaction.response.send_message(
                _("You are not allowed to use this view."),
                ephemeral=True
            )

        return allow
    
    async def wait(self, delete_after: bool = False, edit_after: bool = False) -> bool:
        wait = await super().wait()

        if delete_after and self.msg:
            await self.msg.delete(delay=0)
        elif edit_after and self.msg:
            try:
                await self.msg.edit(view=None)
            except:
                pass #silent fail
        
        return wait