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
from typing import TYPE_CHECKING, overload
from .field import Field
from .reward_pack import RewardPack
from .empty_reward_pack import EmptyRewardPack
from taho.babel import _

if TYPE_CHECKING:
    from typing import List, Callable, Optional, TypeVar, Dict, Literal, Union
    from taho.enums import RewardType
    from discord import Interaction
    from taho.utils import AbstractRewardPack
    from ..form import Form

    T = TypeVar("T")

    RewardTypes = List[
        Dict[
            Literal["reward_types", "conditions"], 
            Union[
                List[RewardType],
                List[Callable[[Form], bool]]
            ]
        ]
    ]

__all__ = (
    "Reward",
)

class Reward(Field):
    @overload
    def __init__(
        self, 
        name: str, 
        label: str, 
        required: bool = ..., 
        reward_types: Optional[List[RewardType]] = ...,
        validators: List[Callable[[str], bool]] = ..., 
        appear_validators: List[Callable[[str], bool]] = ..., 
        default: Optional[T] = None,
        **kwargs
        ) -> None:
        ...
    
    @overload
    def __init__(
        self, 
        name: str, 
        label: str, 
        required: bool = ..., 
        reward_types: Optional[RewardTypes] = ...,
        validators: List[Callable[[str], bool]] = ..., 
        appear_validators: List[Callable[[str], bool]] = ..., 
        default: Optional[T] = None,
        **kwargs
        ) -> None:
        ...
    
    def __init__(
        self, 
        name: str, 
        label: str, 
        required: bool = False, 
        reward_types: Optional[Union[List[RewardType], RewardTypes]] = None,
        validators: List[Callable[[str], bool]] = [], 
        appear_validators: List[Callable[[str], bool]] = [], 
        default: Optional[T] = None,
        **kwargs
        ) -> None:
        super().__init__(
            name, 
            label, 
            required, 
            validators, 
            appear_validators, 
            default, 
            **kwargs)
        
        
        self.original_reward_types = reward_types
        self.reward_types: List[RewardType] = None

        self.value: Optional[List[AbstractRewardPack]] = None
    
    async def get_rewardable_list(self, interaction: Interaction) -> None:
        
        cluster = await self.get_cluster(interaction)

        self.rewardable_list = {
            "stat": [],
            "item": [],
            "role": [],
        }

        def organize(item: T, item_name: str) -> Dict[str, T]:
            return {
                "name": item.name,
                item_name: item,
                "emoji": item.emoji,
            }

        stats = list(map(
            lambda s: organize(s, "stat"),
            await cluster.stats.all()
            ))
        
        items = list(map(
            lambda i: organize(i, "item"),
            await cluster.items.all()
            ))
        
        roles = await cluster.get_roles_by_name(interaction.client)

        roles = list(map(
            lambda r: {
                "name": r,
                "role": roles[r],
                "emoji": None,
            },
            roles
        ))

        self.rewardable_list["stat"] = stats
        self.rewardable_list["item"] = items
        self.rewardable_list["role"] = roles

    async def ask(self, interaction: Interaction) -> None:
        if not hasattr(self, "rewardable_list"):
            await self.get_rewardable_list(interaction)
        
        
        if isinstance(self.original_reward_types, list) and self.original_reward_types \
            and isinstance(self.original_reward_types[0], dict):
            reward_types = None
            for data in self.original_reward_types:
                conditions = data.get("conditions", [])
                form_dict = self.form.to_dict()
                if all(condition(form_dict) for condition in conditions):
                    reward_types = data["reward_types"]
                    break
            if reward_types is None:
                self.reward_types = []
            else:
                self.reward_types = reward_types
        
        else:
            self.reward_types = self.original_reward_types


        from taho.forms import Form

        fields = []
        if self.default:
            for pack in self.default:
                if self.reward_types and pack.type not in self.reward_types:
                    continue
                fields.append(
                    RewardPack(
                        name=pack.name,
                        label=pack.name,
                        reward_types=self.reward_types,
                        default=pack,
                        rewardable_list=self.rewardable_list
                    )
                )
        
        fields.append(
            EmptyRewardPack(
                reward_types=self.reward_types,
                rewardable_list=self.rewardable_list
            )
        )

        form = Form(
            title=_("Rewards"),
            description=_(
                "You can create packs of rewards. A pack is a list "
                "of rewards with the same loot chance and condition.\n"
                "**You can define negative quantities to create a cost.**\n"
                "You can create several packs with the same loot chance and condition."
            ),
            fields=fields,
        )

        for field in form.fields:
            field.form = form

        await form.send(interaction=interaction, ephemeral=True)
        await form.wait()

        if not form.is_canceled():

            self.value = [
                field.value for field in form.fields 
                if not isinstance(field, EmptyRewardPack)
            ]

        await self.display()
    
    async def display(self) -> str:
        if not self.value:
            self.display_value = _("*Unanswered*")

        else:
            guild_id = self.form.guild.id
            self.display_value = []
            for pack in self.value:
                self.display_value.append(_(
                    "**%(pack_name)s:**",
                    pack_name=pack.get_name()
                ))
                for reward in pack.rewards:
                    self.display_value.append(_(
                        "• %(reward_display)s",
                        reward_display=await reward.get_display(guild_id=guild_id),
                    ))
                self.display_value.append("\n")

            self.display_value = "\n".join(self.display_value)
            if len(self.display_value) > 1048:
                self.display_value = self.display_value[:1045] + "..."

        return self.display_value

