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
from discord import ButtonStyle, Interaction, SelectOption
from discord.ui import Select as _Select, select, button
from taho.babel import _
from .field import Field, FieldView
from taho.utils import split_list
from ..choice import Choice

if TYPE_CHECKING:
    from typing import Optional, List, Callable, TypeVar, Dict
    from ..choice import Choice
    from taho.database.models import Role

    T = TypeVar("T")

__all__ = (
    "AccessView",
    "Access",
)

class AccessView(FieldView):
    def __init__(
        self, 
        field: Field, 
        accessible_list: List[List[str, Role]],
        default: Optional[Dict[bool, List[Role]]] = None,
        ) -> None:
        super().__init__(field, default)

        self.accessible_list = accessible_list

        self.accessible_choices = [
            Choice(
                label="@"+role[0],
                value=role[1]
            ) for role in self.accessible_list
        ]

        self.choices_map = {
            c.discord_value:c.value for c in self.accessible_choices
        }

        self.roles_name_map = {
            role[1]: role[0] for role in self.accessible_list
        }

        self.access = default or {
            True: [],
            False: [],
        }

        self.add_or_remove.placeholder = _("Add or remove roles from the list")
        self.add_or_remove.options = [
            SelectOption(
                label=_("Add roles to the list"),
                value="1",
            ),
            SelectOption(
                label=_("Remove roles from the list"),
                value="0",
            ),
        ]

        self.access_type.placeholder = _("The selected roles will have access or not?")
        self.access_type.options = [
            SelectOption(
                label=_("The roles have access"),
                value="1",
            ),
            SelectOption(
                label=_("The roles don't have access"),
                value="0",
            ),
        ]


        self.access_list_placeholder = _("Select roles to add or remove")
        self.select_list = []


        # self.open_modal.placeholder = _("Open the modal to select roles")

        self.adding = True
        self.have_access = True

        self.calculate_refresh()

    def in_access(self) -> List[Role]:
        return self.access[False] + self.access[True]
    
    def calculate_refresh(self) -> None:

        for select in self.select_list:
            self.remove_item(select)
        
        self.select_list = []

        for option in self.add_or_remove.options:
            if option.value == "1" and self.adding == True:
                option.default = True
            elif option.value == "0" and self.adding == False:
                option.default = True
            else:
                option.default = False
        
        for option in self.access_type.options:
            if option.value == "1" and self.have_access == True:
                option.default = True
            elif option.value == "0" and self.have_access == False:
                option.default = True
            else:
                option.default = False

        if self.adding:
            if not self.access_type in self._children:
                self.add_item(self.access_type)


            options = [
                c.to_select_option() for c in self.accessible_choices
                if c.value not in self.in_access()
            ]
            options = split_list(options, 25)

            if len(options) > 2:
                raise ValueError("Too many options") #todo implement in this case

            for _options in options:
                select = _Select(
                    options=_options,
                    placeholder=self.access_list_placeholder,
                    min_values=1,
                    max_values=len(_options),
                )
                select.callback = self.access_list
                self.select_list.append(select)
                self.add_item(select)

        else:
                
            self.remove_item(self.access_type)

            options = [
                c.to_select_option() for c in self.accessible_choices
                if c.value in self.in_access()
            ]

            for option in options:
                c = self.choices_map[option.value]
                if c in self.access[True]:
                    option.description = _("This role have access")
                else:
                    option.description = _("This role don't have access")
                
            options = split_list(options, 25)

            if len(options) > 2:
                raise ValueError("Too many options") #todo implement in this case
            
            for _options in options:
                select = _Select(
                    options=_options,
                    placeholder=self.access_list_placeholder,
                    min_values=1,
                    max_values=len(_options),
                )
                select.callback = self.access_list
                self.select_list.append(select)
                self.add_item(select)

    async def access_to_string(self) -> str:
        string = _(
            "The access is a list of roles that can/cannot "
            "use what you are creating.\n\n"
            )
        if not self.access[False] and not self.access[True]:
            string += _("**No roles are configured.**\n\n")
        else:
            string = ""
            if self.access[True]:
                role_list = ", ".join(
                    "@"+self.roles_name_map[role] for role in self.access[True]
                )
                string += _(
                    "The roles with access are: **%(role_list)s**\n\n",
                    role_list=role_list
                )
            if self.access[False]:
                role_list = ", ".join(
                    "@"+self.roles_name_map[role] for role in self.access[False]
                )
                string += _(
                    "The roles without access are: **%(role_list)s**\n\n",
                    role_list=role_list
                )
        return string + _(
            "You can add roles to the access list by selecting "
            "the **Add roles to the list** option, then selecting "
            "the type of access, and the roles you want."
        )

    async def refresh(self, interaction: Interaction) -> None:
        self.calculate_refresh()
        content = await self.access_to_string()
        await interaction.response.edit_message(
            content=content,
            view=self,
        )

    @select(
        placeholder="add_or_remove",
        min_values=1,
        max_values=1,
    )
    async def add_or_remove(self, interaction: Interaction, _) -> None:
        if self.add_or_remove.values[0] == "1":
            self.adding = True
        else:
            self.adding = False
        
        await self.refresh(interaction)
    
    @select(
        placeholder="access_type",
        min_values=1,
        max_values=1,
    )
    async def access_type(self, interaction: Interaction, _) -> None:
        if self.access_type.values[0] == "1":
            self.have_access = True
        
        else:
            self.have_access = False
        
        await interaction.response.edit_message()

    async def access_list(self, interaction: Interaction) -> None:

        values = []
        for select in self.select_list:
            values += select.values
        
        roles = [self.choices_map[value] for value in values]

        if self.adding:
            self.access[self.have_access] += roles
        
        else:
            self.access[self.have_access] = [
                role for role in self.access[self.have_access]
                if not role in roles
            ]

        await self.refresh(interaction)
    
    @button(
        label="finish",
        style=ButtonStyle.green,
        row=4
    )
    async def finish(self, interaction: Interaction, _) -> None:
        await self.on_submit(interaction)
    
    async def on_submit(self, interaction: Interaction) -> None:
        self.field.value = self.access
        self.field.default = self.access
        await interaction.response.edit_message(
            content=_("The access list has been updated."),
            view=None
            )

        await super().on_submit(interaction)


class Access(Field):
    def __init__(
        self, 
        name: str, 
        label: str, 
        required: bool = False, 
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
        
    async def get_accessible_list(self, interaction: Interaction) -> None:
        cluster = await super().get_cluster(interaction)

        # users = await cluster.get_users_by_name(interaction.client)
        # users = [[name, user] for name, user in users.items()]

        roles = await cluster.get_roles_by_name(interaction.client)
        roles = [[name, role] for name, role in roles.items()]

        self.accessible_list = roles
    
    async def ask(self, interaction: Interaction) -> None:
        if not hasattr(self, "accessible_list"):
            await self.get_accessible_list(interaction)

        view = AccessView(
                field=self,
                accessible_list=self.accessible_list,
                default=self.default
            )
        
        content = await view.access_to_string()
        await interaction.response.send_message(
            content=content,
            embed=None,
            view=view,
            ephemeral=True,
        )
        await view.wait()


    
    async def display(self) -> str:
        if not self.value[True] and not self.value[False]:
            self.display_value = _("*Unanswered*")
        else:
            roles_name_map = {
                role[1]: role[0] for role in self.accessible_list
            }
            self.display_value = ""
            if self.value[True]:
                role_list = ", ".join(
                    "@"+roles_name_map[role] for role in self.value[True]
                )

                self.display_value += _(
                    "✅: **%(role_list)s**\n",
                    role_list=role_list
                )
            if self.value[False]:
                role_list = ", ".join(
                    "@"+roles_name_map[role] for role in self.value[False]
                )
                self.display_value += _(
                    "❌: **%(role_list)s**\n",
                    role_list=role_list
                )
        
        return self.display_value
