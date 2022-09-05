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
from taho.database.db_utils import get_link_field

if TYPE_CHECKING:
    from typing import TypeVar, Dict, Union, Type
    from taho.database.models import MODEL, Stat

    T = TypeVar("T")
    U = TypeVar("U")

__all__ = (
    "AbstractClassStat",
)

class AbstractClassStat:
    """
    Represents an abstract class stat.

    Used to fill the :class:`~taho.forms.fields.Stat` field.

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
        stat: Stat,
        value: int = None
    ) -> None:
        self.stat = stat
        self.value = value
    
    
    def to_dict(self) -> Dict[str, Union[str, T]]:
        """
        Returns a dictionary representation of the stat.
        """
        return {
            "stat": self.stat,    
            "value": self.value
        }
    
    async def to_db_stat(self, stat_type: Type[U], link: MODEL) -> U:
        """|coro|

        Converts this abstract stat to a stat
        of another type, in the DB.

        Example: Convert an :class:`.AbstractClassStat` to a 
        :class:`~taho.database.models.ClassStat`.

        Parameters
        -----------
        stat_type:
            The type of stat to convert to.
        link: :class:`.BaseModel`
            The additional data to do the link between 
            the two stats.
        
        Returns
        --------
            The converted stat.
        """
        link_field = get_link_field(stat_type)
        
        self_dict = self.to_dict()
        self_dict[link_field] = link

        return await stat_type.create(
            **self_dict
        )

    async def get_display(self) -> str:
        """|coro|

        Returns the display of the stat.

        Returns
        --------
        :class:`str`
            The stat's display string.
        """
        if hasattr(self, "_display"):
            return self._display

        self._display = _(
            "*%(stat_display)s*: **%(value)s**",
            stat_display=self.stat.get_display(),
            value=self.value if self.value is not None else _("Unanswered")
        )

        return self._display 

