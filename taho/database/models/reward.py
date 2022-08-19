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
from .base import BaseModel
from tortoise import fields
from tortoise.validators import MinValueValidator, MaxValueValidator
from taho.enums import RewardType
from taho.utils.abstract import AbstractReward, AbstractRewardPack


if TYPE_CHECKING:
    from typing import Union, Tuple
    from taho.abc import StuffShortcutable

__all__ = (
    "RewardPack",
    "Reward",
)

class RewardPack(BaseModel):
    """
    Represents a reward pack.

    .. container:: operations

        .. describe:: x == y

            Checks if two reward packs are equal.

        .. describe:: x != y

            Checks if two reward packs are not equal.
        
        .. describe:: hash(x)

            Returns the reward pack's hash.
        
        .. describe:: str(x)

            Returns the reward pack's name.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: type

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.RewardType`
            
            Python: :class:`~taho.enums.RewardType`
        
        .. collapse:: luck

            Tortoise: :class:`tortoise.fields.DecimalField`

                - :attr:`max_digits` ``1``
                - :attr:`decimal_places` ``4``
                - :attr:`default` 1
            
            Python: :class:`float`
    
    Attributes
    -----------
    id: :class:`int`
        The reward pack's ID.
    type: :class:`~taho.enums.RewardType`
        The reward's type.
    luck: :class:`float`
        The reward pack's luck.
    rewards: List[:class:`.Reward`]
        |coro_attr|

        The rewards included in the reward pack.
    """
    class Meta:
        abstract = True
    
    id = fields.IntField(pk=True)

    type = fields.IntEnumField(RewardType, null=True)

    luck = fields.FloatField(default=1, validators=[MinValueValidator(0), MaxValueValidator(1)])

    rewards: fields.ReverseRelation["Reward"]

    async def to_abstract(self) -> AbstractRewardPack:
        """|coro|

        Returns the reward pack as an abstract reward pack.

        Returns
        --------
        :class:`~taho.utils.AbstractRewardPack`
            The abstract reward pack.
        """
        return AbstractRewardPack(
            type=self.type,
            luck=self.luck,
            rewards=[await reward.to_abstract() async for reward in self.rewards]
        )

class Reward(BaseModel):
    """
    Represents a reward.

    .. container:: operations

        .. describe:: x == y

            Checks if two rewards are equal.

        .. describe:: x != y

            Checks if two rewards are not equal.
        
        .. describe:: hash(x)

            Returns the reward's hash.
        
        .. describe:: str(x)

            Returns the reward's name.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: pack

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`.RewardPack`
                - :attr:`related_name` ``rewards``
            
            Python: :class:`~taho.database.models.RewardPack`
        
        .. collapse:: stuff_shortcut

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.StuffShortcut`
            
            Python: :class:`~taho.database.models.StuffShortcut`
        
        .. collapse:: regeneration

            Tortoise: :class:`tortoise.fields.BooleanField`

                - :attr:`default` ``False``
            
            Python: :class:`bool`
        
        .. collapse:: durability

            Tortoise: :class:`tortoise.fields.BooleanField`

                - :attr:`default` ``False``
            
            Python: :class:`bool`
        
        .. collapse:: min_amount

            Tortoise: :class:`tortoise.fields.DecimalField`

                - :attr:`max_digits` ``10``
                - :attr:`decimal_places` ``2``
                - :attr:`default` ``1``
            
            Python: :class:`float`
        
        .. collapse:: max_amount

            Tortoise: :class:`tortoise.fields.DecimalField`

                - :attr:`max_digits` ``10``
                - :attr:`decimal_places` ``2``
                - :attr:`null` ``True``
            
            Python: :class:`float`

    Attributes
    -----------
    id: :class:`int`
        The reward's ID.
    pack: :class:`.RewardPack`
        The reward's pack.
    stuff_shortcut: :class:`~taho.database.models.StuffShortcut`
        The reward's shortcut.
    regeneration: :class:`bool`
        If the shortcut points to a :class:`~taho.database.models.Stat`,
        then this is whether the stat should be regenerated.
    durability: :class:`bool`
        If the shortcut points to a :class:`~taho.database.models.Item`,
        then this is whether it should add durability to it.
    min_amount: :class:`float`
        The minimum amount of the reward.
    max_amount: Optional[:class:`float`]
        The maximum amount of the reward.
    

    .. note::

        If ``max_amount`` is ``None``, then the reward 
        amount is fixed to ``min_amount``.
    """
    class Meta:
        abstract = True
    
    id = fields.IntField(pk=True)

    pack = fields.ForeignKeyField("main.RewardPack", related_name="rewards")
    stuff_shortcut = fields.ForeignKeyField("main.StuffShortcut")
    regeneration = fields.BooleanField(default=False)
    durability = fields.BooleanField(default=False)
    min_amount = fields.DecimalField(max_digits=10, decimal_places=2, default=1)
    max_amount = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    async def get_stuff(self, force: bool = False) -> StuffShortcutable:
        from taho.database.db_utils import get_stuff # avoid circular import

        return await get_stuff(self, force=force)
    
    async def get_stuff_amount(self, force: bool = False) -> Tuple[Union[int, float]]:
        from taho.database.db_utils import get_stuff_amount # avoid circular import

        amount = await get_stuff_amount(self, force=force)

        # Case: stuff_shortcut points to a Role
        if amount == 1:
            setattr(self, "_amount", (1,1))
            return self._amount

        return amount
    
    async def to_abstract(self) -> AbstractReward:
        """|coro|

        Returns the reward as an abstract reward.

        Returns
        --------
        :class:`~taho.utils.AbstractReward`
            The abstract reward.
        """
        return AbstractReward(
            stuff=await self.stuff,
            regeneration=self.regeneration,
            durability=self.durability,
            min_amount=self.min_amount,
            max_amount=self.max_amount
        )
