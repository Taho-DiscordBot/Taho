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
    "RewardType",
    "get_reward_type_text",
)

class RewardType(IntEnum):
    passive = 0
    active = 1
    equip = 2

def get_reward_type_text(reward_type: RewardType) -> str:
    """
    Get the text of a reward type.

    Parameters
    -----------
    reward_type: :class:`.RewardType`
        The reward type.
    
    Raises
    -------
    ValueError
        If the reward type is invalid.
    
    Returns
    --------
    :class:`str`
        The text of the reward type.
    """
    from taho.babel import _

    texts = {
        RewardType.passive: _("Passive (when owned)"),
        RewardType.active: _("Active (when used)"),
        RewardType.equip: _("Equip (when equipped to the hotbar)"),

    }
    return texts[reward_type]