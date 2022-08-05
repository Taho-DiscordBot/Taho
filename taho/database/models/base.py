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
from tortoise.models import Model

__all__ = (
    "BaseModel",
)

class BaseModel(Model):
    class Meta:
        abstract = True
    
    def get_fields(self) -> List[dict]:
        desc = self.describe(serializable=True)
        return [
            field
            for field in chain(
                desc.get("data_fields", []),
                desc.get("fk_fields", []),
                desc.get("o2o_fields", []),
            )
        ]
    
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)
    
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
    
    def __repr__(self) -> str:
        return super().__repr__()
    
    def __hash__(self) -> int:
        return hash(self.__repr__())