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
from ctypes import Union
from typing import TYPE_CHECKING
import discord
import emojis

if TYPE_CHECKING:
    from typing import Optional, Dict, TypeVar
    import discord
    from taho import Bot

    T = TypeVar("T")


__all__ = (
    "Emoji",
)

class Emoji:
    """Represents an Emoji.

    .. container:: operations

        .. describe:: x == y

            Checks if two emojis are equal.
        
        .. describe:: x != y

            Checks if two emojis are not equal.
        
        .. describe:: bool(x)

            Checks if the emoji exists.
        
        .. describe:: hash(x)

            Returns the hash of the emoji.
        
        .. describe:: str(x)

            Returns the emoji rendered for discord.
    
    Attributes
    ----------
    id: Optional[:class:`int`]
        The id of the emoji.
        Only set if the emoji is a custom emoji.
    name: :class:`str`
        The name of the emoji.
        Empty if the emoji does not exist.
    animated: :class:`bool`
        Whether the emoji is animated.
    url: Optional[:class:`str`]
        The url of the emoji.
        Only set if the emoji is a custom emoji.    
    """

    __slots__ = ('animated', 'name', 'id', 'url')

    def __init__(self, client: Bot, emoji: T) -> None:
        self.animated: bool = None
        self.name: str = ""
        self.id: Optional[int] = None
        self.url: Optional[str] = None
        self._init_emoji(client, emoji)

    def __str__(self) -> str:
        if self.id is None:
            return self.name
        if self.animated:
            return f'<a:{self.name}:{self.id}>'
        return f'<:{self.name}:{self.id}>'
    
    def __repr__(self):
        return f"<Emoji id={self.id} name={self.name} animated={self.animated}>"

    def __eq__(self, other: object) -> bool:
        if not self.is_custom():
            return isinstance(other, Emoji) and self.name == other.name
        if isinstance(other, Emoji):
            return self.id == other.id
        return False
    
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
    
    def __bool__(self) -> bool:
        return bool(self.name)

    def __hash__(self) -> int:
        return hash((self.id, self.name))
    
    def is_custom(self) -> bool:
        """:class:`bool`: Checks if this is a custom emoji."""
        return self.id is not None
    
    def _init_emoji(self, bot: Bot, value: T) -> None:
        """
        Get data from the emoji and set the attributes.


        .. note::
            This method is called by the constructor.
            Please do not call this method yourself.

        Parameters
        ----------
        value:
            The raw emoji (id, name, etc.) to get the data from.
        bot: :class:`~taho.Bot`
            The bot instance.
            It is used to get the emoji from Discord.
        """
        if not value:
            return

        # The value is a Discord Emoji object.
        if isinstance(value, discord.Emoji) or isinstance(value, discord.PartialEmoji):

            emoji = value

            self.id = emoji.id
            self.name = emoji.name
            self.url = str(emoji.url)
            self.animated = emoji.animated
        
        elif isinstance(value, str):
            value = emojis.encode(value)

            # The value is a unicode emoji.
            if emojis.count(value) > 0:
                emoji = emojis.get(value)[0]
                self.name = emoji

            # The value is a custom emoji, in a specific format:
            # <:name:id>
            # or <a:name:id>
            elif discord.PartialEmoji.from_str(value).id is not None:
                emoji = discord.PartialEmoji.from_str(value)
                self.id = emoji.id
                self.name = emoji.name
                self.url = str(emoji.url)
                self.animated = emoji.animated
            
            # The value is an id of a custom emoji.
            else:
                try:
                    emoji_id = int(value)
                except ValueError:
                    # The value is not a valid emoji
                    return
                else:
                    emoji = bot.get_emoji(emoji_id)
                    emoji = bot.get_emoji(emoji_id)
                    if not emoji:
                        # The emoji does not exist.
                        return 
                    self.id = emoji.id
                    self.name = emoji.name
                    self.url = str(emoji.url)
                    self.animated = emoji.animated
    
    def partial(self) -> discord.PartialEmoji:
        """
        
        Get the Emoji as a :class:`discord.PartialEmoji` object.

        Attributes
        ----------

        Raises
        ------

        Returns
        -------
        :class:`discord.PartialEmoji`
            The :class:`discord.PartialEmoji` object.

        """
        return discord.PartialEmoji(self.name, self.animated, self.id)
    
    def to_dict(self) -> Dict[str, Union[int, str, bool]]:
        """
        
        Returns the Emoji as a dictionary.

        Attributes
        ----------

        Raises
        ------

        Returns
        -------
        Dict[:class:`str`, Union[:class:`int`, :class:`str`, :class:`bool`]]
            The dictionary.
        """
        return {
            "id": self.id,
            "name": self.name,
            "animated": self.animated,
            "url": self.url,
            "repr": str(self)
        }