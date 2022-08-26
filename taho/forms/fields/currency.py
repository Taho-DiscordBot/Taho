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
from discord import Interaction
from taho.babel import _
from taho.database.models import Cluster, Currency as _Currency
from taho.forms.fields.select import Select
from ..choice import Choice

if TYPE_CHECKING:
    from typing import Optional, List, TypeVar, Union

    T = TypeVar("T")

__all__ = (
    "Currency",
)

class Currency(Select):
    def __init__(
        self,
        *args, 
        cluster: Union[int, Cluster] = None,
        db_filters: Optional[dict] = {},
        **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if isinstance(cluster, Cluster):
            self.cluster = cluster.id
        else:
            self.cluster = cluster
        
        self.db_filters = db_filters
    
    async def get_choices(self, interaction: Interaction = None) -> bool:
        currencies: List[_Currency] = await _Currency.filter(cluster_id=self.cluster, **self.db_filters).all()
        if not currencies:
            return await super().get_choices(interaction)
        else:
            self.choices = [
                Choice(
                    label=currency.name, 
                    value=currency,
                    emoji=currency.emoji
                ) for currency in currencies
            ]
            if self.value:
                values = self.value if isinstance(self.value, list) else [self.value]
                for value in values:
                    if not value in currencies:
                        self.choice.append( Choice(
                        label=value.name,
                        value=value,
                        emoji=value.emoji
                    ))
            
            if self.max_values == -1:
                self.max_values = len(self.choices)
            return True

