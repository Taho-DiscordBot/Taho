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
from taho.babel import _

if TYPE_CHECKING:
    from typing import TypeVar, Dict, Union, Type
    from taho.database.models import MODEL, AccessRuleShortcut
    from taho.abc import AccessRuleShortcutable
    from taho.bot import Bot

    T = TypeVar("T")
    U = TypeVar("U")

__all__ = (
    "AbstractAccessRule",
)

class AbstractAccessRule:
    """
    Represents an abstract access rule.

    Used to fill the :class:`~taho.forms.fields.AccessRule` field.

    Attributes
    -----------
    have_access: :class:`bool`
        Whether the access is granted.
    access_shortcut: Optional[:class:`.AccessRuleShortcut`]
        The shortcut to the entity who have access.
    access: Optional[:class:`.AccessRuleShortcutable`]
        The entity who have access.
    """
    def __init__(
        self,
        have_access: bool = False,
        access: AccessRuleShortcutable = None,
        access_shortcut: AccessRuleShortcut = None,
    ) -> None:
        if not access and not access_shortcut:
            raise ValueError("Either access or access_shortcut must be set.")
        self.access = access
        self.access_shortcut = access_shortcut
        self.have_access = have_access
    
    def to_dict(self) -> Dict[str, Union[AccessRuleShortcut, AccessRuleShortcutable, bool, None]]:
        """
        Returns a dictionary representation of the access.
        """
        return {
            "access": self.access,
            "access_shortcut": self.access_shortcut,
            "have_access": self.have_access,
        }
    
    async def to_db_access(self, access_type: Type[T], link: MODEL) -> T:
        """|coro|

        Converts this abstract access rule to an access rule
        of another type, in the DB.

        Example: Convert a :class:`.AbstractAccessRule` to an 
        :class:`~taho.database.models.ItemAccessRule`.

        Parameters
        -----------
        access_type:
            The type of access rule to convert to.
        link: :class:`.BaseModel`
            The additional data to do the link between 
            the two access rules.
        
        Returns
        --------
            The converted access rule.
        """

        link_field = [
            f["name"] for f in access_type.get_fields() 
            if f["field_type"] == "ForeignKeyField"
            ][0]
        
        self_dict = self.to_dict()
        self_dict[link_field] = link

        return await access_type.create(
            **self_dict
        )

    async def get_display(self, bot: Bot = None, guild_id: int = None) -> str:
        """|coro|

        Returns the display of the reward.
        """
        if hasattr(self, "_display"):
            return self._display

        if not bot:
            from ..utils.utils_ import get_bot
            bot = get_bot()

        from taho.database.models import Role

        access = self.access or await self.access_shortcut.get()

        if isinstance(access, Role):
            access_str = await access.get_display(bot, server_id=guild_id)
        
        if self.have_access:
            self._display = _("✅ %(entity)s", entity=access_str)
        else:
            self._display = _("❌ %(entity)s", entity=access_str)

        return self._display 

