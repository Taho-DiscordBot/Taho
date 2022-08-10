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
from discord.app_commands import Translator
from taho.babel import discord_translator_gettext
from babel import Locale


if TYPE_CHECKING:
    from discord.app_commands import locale_str, TranslationContext
    from discord import Locale as DiscordLocale
    from typing import Optional

__all__ = (
    "TahoTranslator",
)

class TahoTranslator(Translator):
    async def translate(
        self, 
        string: locale_str, 
        locale: DiscordLocale, 
        context: TranslationContext
        ) -> Optional[str]:
        locale = Locale.parse(locale.value, sep="-")
        
        translation = await discord_translator_gettext(string.message, locale=locale)

        return translation if translation != string.message else None