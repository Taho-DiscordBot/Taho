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
from taho.database.db_utils import value_to_json, get_link_field

if TYPE_CHECKING:
    from typing import TypeVar, Dict, Union, Type
    from taho.database.models import MODEL

    T = TypeVar("T")
    U = TypeVar("U")

__all__ = (
    "AbstractInfo",
)

class AbstractInfo:
    """
    Represents an abstract info.

    Used to fill the :class:`~taho.forms.fields.Infos` field.

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
        key: str,
        value: T,
    ) -> None:
        self.key = key
        self.value = value
    
    
    def to_dict(self) -> Dict[str, Union[str, T]]:
        """
        Returns a dictionary representation of the info.
        """
        return {
            "key": self.key,
            "value": str(self.value),
            "type": get_type(self.value),
        }
    
    async def to_db_info(self, info_type: Type[U], link: MODEL) -> U:
        """|coro|

        Converts this abstract info to an info
        of another type, in the DB.

        Example: Convert an :class:`.AbstractInfo` to a 
        :class:`~taho.database.models.BankInfo`.

        Parameters
        -----------
        info_type:
            The type of info to convert to.
        link: :class:`.BaseModel`
            The additional data to do the link between 
            the two infos.
        
        Returns
        --------
            The converted info.
        """

        link_field = [
            f["name"] for f in info_type.get_fields() 
            if f["field_type"] == "ForeignKeyField"
            ][0]
        
        self_dict = self.to_dict()
        self_dict[link_field] = link

        return await info_type.create(
            **self_dict
        )

    async def get_display(self) -> str:
        """|coro|

        Returns the display of the info.

        Returns
        --------
        :class:`str`
            The info's display string.
        """
        if hasattr(self, "_display"):
            return self._display

        from taho.babel import get_info_text

        self._display = _(
            "*%(info_text)s*: **%(value)s",
            info_text=await get_info_text(self.key),
            value=str(self.value)
        )

        return self._display 

