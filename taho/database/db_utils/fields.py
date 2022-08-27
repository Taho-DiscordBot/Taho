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

if TYPE_CHECKING:
    from typing import Optional, Type
    from ..models import BaseModel

__all__ = (
    "get_link_field",
)

def get_link_field(model: Type[BaseModel]) -> Optional[str]:
    """
    Get the "link field" of a DB model,
    the ForeignKey field.
    Used for Abstract Models.

    Parameters
    -----------
    Type[:class:`~taho.database.models.BaseModel`]
        The model to get the field from.
    
    Returns
    --------
    Optional[:class:`str`]
        The link field, if exists.
    """
    link_field = [
        f["name"] for f in model.get_fields() 
        if f["field_type"] in ("ForeignKeyField", "ForeignKeyFieldInstance") \
            and not "shortcut" in f["name"]
    ]
    if link_field:
        return link_field[0]
    else:
        return None