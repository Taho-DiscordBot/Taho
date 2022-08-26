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
from taho.database.models import Item as _Item
from taho.enums import ItemType
from taho.database import db_utils
from .select import Select

if TYPE_CHECKING:
    from typing import Optional, List, Callable, TypeVar
    from discord import Interaction
    from ..choice import Choice

    T = TypeVar("T")

__all__ = (
    "Item",
)

class Item(Select):
    def __init__(
        self, 
        name: str, 
        label: str, 
        item_types: List[ItemType],
        description: str = None,
        required: bool = False,
        validators: List[Callable[[str], bool]] = [], 
        appear_validators: List[Callable[[str], bool]] = [], 
        default: Optional[T] = None,
        min_values : Optional[int] = 1,
        max_values: Optional[int] = 1,
        **kwargs
    ) -> None:
        super().__init__(
            name=name,
            label=label,
            description=description,
            required=required,
            validators=validators,
            appear_validators=appear_validators,
            default=default,
            min_values=min_values,
            max_values=max_values,
            **kwargs)
        
        self.item_types = item_types
    
    async def get_choices(self, interaction: Interaction = None) -> None:
        cluster = await db_utils.get_cluster(
                interaction.client, 
                interaction.guild
            )
        item_list = await _Item.filter(
            cluster__id=cluster.id,
            type__in=self.item_types
        )
        if item_list.count() == 0 and interaction:
            await interaction.response.send_message(
                _("No items available.")
            )
            return False
        elif item_list.count() == 0:
            return False
        choices = []
        for item in item_list:
            choices.append(
                Choice(
                    label=item.name,
                    value=item,
                    description=item.description,
                    emoji=item.emoji
                )
            )
        self.choices = choices
        return True
    