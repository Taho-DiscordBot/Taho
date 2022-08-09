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
from taho.enums import RewardType, get_reward_type_text
from taho.babel import _

if TYPE_CHECKING:
    from typing import Optional, List, TypeVar, Dict, Union
    from taho.database.models import BaseModel, StuffShortcut
    from taho.abc import StuffShortcutable

    T = TypeVar("T")
    U = TypeVar("U")

__all__ = (
    "AbstractRewardPack",
    "AbstractReward",
)

class AbstractRewardPack:
    """
    Represents an abstract reward pack.

    Used to fill the :class:`~taho.forms.fields.Reward` field.

    Attributes
    -----------
    type: :class:`.RewardType`
        The type of reward pack.
    luck: float
        The luck of the reward pack.
    rewards: List[:class:`.AbstractReward`]
        The rewards in the reward pack.
    """
    def __init__(
        self,
        type: Optional[RewardType] = None,
        luck: Optional[float] = 1.0,
        rewards: List[AbstractReward] = [],
        ) -> None:
        self.type = type
        self.luck = luck
        self.rewards = rewards
    
    def add_reward(self, reward: AbstractReward) -> None:
        """

        Adds a reward to the reward pack.

        Parameters
        -----------
        reward: :class:`.StuffShortcutable`
            The reward to add.
        """
        self.rewards.append(reward)
    
    def clear_rewards(self) -> None:
        """

        Clears the rewards in the reward pack.
        """
        self.rewards.clear()
    
    def delete_reward(self, reward: AbstractReward) -> None:
        """

        Deletes a reward from the reward pack.

        Parameters
        -----------
        reward: :class:`.StuffShortcutable`
            The reward to delete.
        """
        try:
            self.rewards.remove(reward)
        except ValueError:
            pass

    async def to_db_pack(self, pack_type: T, reward_type: type, link: BaseModel) -> T:
        """|coro|

        Converts this abstract reward pack to a reward pack
        of another type, in the DB.

        Example: Convert a :class:`.RewardPack` to an 
        :class:`~taho.database.models.ItemRewardPack`.

        Parameters
        -----------
        pack_type:
            The type of reward pack to convert to.
        reward_type:
            The type of reward to convert to.
        link: :class:`.BaseModel`
            The additional data to do the link between 
            the two reward packs.
        
        Returns
        --------
        
            The converted reward pack.
        
        Examples
        ---------

        You want to convert a :class:`.RewardPack` to an
        :class:`~taho.database.models.ItemRewardPack`.

        .. code-block:: python3

            from taho.database.models import RewardPack, ItemRewardPack, ItemReward, Item

            item: Item
            reward_pack: RewardPack

            item_reward_pack = await reward_pack.to_other_pack(ItemRewardPack, ItemReward, item)
        """

        link_field = [
            f["name"] for f in pack_type.get_fields() 
            if f["field_type"] == "ForeignKeyField"
            ][0]

        new_pack = await pack_type.create(
            type=self.type,
            luck=self.luck,
            **{
                link_field: link,
            }
        )
        rewards = [
            reward.to_db_reward(reward_type, new_pack) for reward in self.rewards
        ]
        await reward_type.bulk_create(rewards)

        return new_pack

    def get_name(self) -> str:
        name = _(
            "%(luck)s %%", 
            luck=self.luck
            )
        if self.type:
            name += " - "
            name += get_reward_type_text(self.type)
        return name

class AbstractReward:
    """
    Represents an abstract reward.

    Used to fill the :class:`~taho.forms.fields.Reward` field.

    Attributes
    -----------
    stuff: :class:`.StuffShortcutable`
        The stuff to reward.
    stuff_shortcut: :class:`.StuffShortcut`
        The shortcut to the stuff to reward.
    regeneration: :class:`bool`
        If the stuff is a :class:`~taho.database.models.Stat` 
        and should be regenerated.
    durability: :class:`bool`
        If the stuff is a :class:`~taho.database.models.Item` 
        and should be regenerated.
    min_amount: :class:`float`
        The minimum amount of the stuff to reward.
    max_amount: Optional[:class:`float`]
        The maximum amount of the stuff to reward.
        If not set, the minimum amount will be used
        to make a fix amount.
    """
    def __init__(
        self,
        stuff: StuffShortcutable = None,
        stuff_shortcut: StuffShortcut = None,
        regeneration: bool = False,
        durability: bool = False,
        min_amount: float = 1,
        max_amount: float = None,
    ) -> None:
        if not stuff and not stuff_shortcut:
            raise ValueError("Either stuff or stuff_shortcut must be set.")
        self.stuff = stuff
        self.stuff_shortcut = stuff_shortcut
        self.regeneration = regeneration
        self.durability = durability
        self.min_amount = min_amount
        self.max_amount = max_amount
    
    def to_dict(self) -> Dict[str, Union[StuffShortcut, StuffShortcutable, bool, float, None]]:
        """
        Returns a dictionary representation of the reward.
        """
        return {
            "stuff": self.stuff,
            "stuff_shortcut": self.stuff_shortcut,
            "regeneration": self.regeneration,
            "durability": self.durability,
            "min_amount": self.min_amount,
            "max_amount": self.max_amount,
        }
    
    def to_raw_db_reward(self, pack: T, reward_type: U) -> U:
        return reward_type(
            pack_id=pack.id,
            **self.to_dict()
        )
    
    async def to_db_reward(self, pack: T, reward_type: U) -> U:
        """|coro|

        Converts this abstract reward to a reward
        of another type, in the DB.

        Example: Convert a :class:`.Reward` to an 
        :class:`~taho.database.models.ItemReward`.

        Parameters
        -----------
        reward_type:
            The type of reward to convert to.
        
        Returns
        --------
        
            The converted reward.
        
        Examples
        ---------

        You want to convert a :class:`.Reward` to an
        :class:`~taho.database.models.ItemReward`.

        .. code-block:: python3

            from taho.database.models import Reward, ItemReward, Item

            item: Item
            reward: Reward

            item_reward = await reward.to_other_reward(ItemReward, item)
        """

        reward = self.to_raw_db_reward(pack, reward_type)
        await reward.save()

        return reward

