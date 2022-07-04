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
from enum import IntEnum

__all__ = (
    "RegenerationType",
    "RPEffect",
)

class RegenerationType(IntEnum):
    """
    Represents the regeneration types of a stat.
    """
    no_regeneration = 0
    no_regen = 0
    regeneration = 1
    regen = 1
    not_natural_regeneration = 2
    not_natural_regen = 2

class RPEffect(IntEnum):
    """
    Represents the RP effects of a stat.
    """
    no_effect = 0
    hp = 1
    stamina = 2
    strength = 3
    protection = 4
    speed = 5
    agility = 6
    ability = 7