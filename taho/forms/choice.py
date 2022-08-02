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
import uuid
from taho.babel import _
from discord import SelectOption


if TYPE_CHECKING:
    from typing import Optional, TypeVar
    from taho import Emoji

    T = TypeVar("T")

__all__ = (
    "Choice",
)

class Choice:
    def __init__(
        self, 
        label: str, 
        value: T,
        *,
        selected: bool = False,
        description: Optional[str] = None,
        emoji: Optional[Emoji] = None,
    ) -> None:
        self.label = label
        self.value = value

        self.discord_value = self._get_discord_value()
        self.selected = selected
        self.description = description
        self.emoji = emoji
    
    def _get_discord_value(self) -> str:
        return str(uuid.uuid4())
    
    def to_select_option(self) -> SelectOption:
        if self.emoji:
            emoji = self.emoji.to_partial()
        else:
            emoji = None
        return SelectOption(
                label=self.label,
                value=self.discord_value,
                default=self.selected,
                description=self.description,
                emoji=emoji,
            )
