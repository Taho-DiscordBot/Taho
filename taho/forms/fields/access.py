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
import traceback
from typing import TYPE_CHECKING
from discord import Interaction, ui, SelectOption, ButtonStyle
from taho.babel import _
from taho.utils.utils_ import split_list
from taho.database.models import Item
from .field import Field, FieldView
from ..choice import Choice
from taho.utils.abstract import AbstractAccessRule

if TYPE_CHECKING:
    from typing import List, Callable, Optional, Dict, Any
    from taho.database.models import Role

    AccessibleList = List[List[str, Role]]

__all__ = (
    "AccessRule",
)

class AccessRuleView(FieldView):
    def __init__(
        self, 
        field: AccessRule, 
        ) -> None:
        default = field.value
        super().__init__(field, default)
        self.accessible_list = self.field.accessible_list
        self.value = self.default

        self.action.placeholder = _("What do you want to do?")
        self.action_options = {
            "add": SelectOption(
                label=_("Add a rule"),
                value="add",
            ),
            "remove": SelectOption(
                label=_("Remove a rule"),
                value="remove",
            ),
        }

        self.finish.label = _("Finish")

        self.check_action_options()
    
    def check_action_options(self) -> None:
        self.value = self.field.value
        if self.value:
            self.action.options = list(self.action_options.values())
        else:
            self.action.options = [
                self.action_options["add"],
                ]
        
    async def get_content(self) -> str:
        guild_id = self.field.form.guild.id
        if not self.value:
            rule_list = [
                _("**No rules have been set yet.**"),
            ]
        else:
            rule_list = [
                await rule.get_display(guild_id=guild_id)
                for rule in self.value
            ]
        return _(
            "The access is a list of roles that can/cannot "
            "use what you are creating.\n\n"
            "%(rule_list)s\n\n"
            "You can add roles to the access list by selecting "
            "the **Add roles to the list** option, then selecting "
            "the type of access, and the roles you want.",
            rule_list="\n".join(rule_list),
        )

    @ui.select(
        placeholder="what do you want to do?",
        options=[],
    )
    async def action(self, interaction: Interaction, _) -> None:
        try:
            action = self.action.values[0]
            actions_views = {
                "add": {
                    "view": AccessRuleViewAdd,
                    "func": "add_rule",
                },
                "remove": {
                    "view": AccessRuleViewRemove,
                    "func": "remove_rule",
                },
            }

            data = actions_views[action]

            view = data["view"](self)

            func = getattr(view, data["func"])
            await func(interaction)
        except Exception:
            print(traceback.format_exc())
    
    @ui.button(
        label="finish",
        style=ButtonStyle.green
    )
    async def finish(self, interaction: Interaction, _) -> None:
        return await self.on_submit(interaction, edit_message=True)
    
    async def refresh(self, interaction: Interaction) -> None:
        self.check_action_options()

        content = await self.get_content()
        await interaction.response.edit_message(
            content=content,
            view=self,
        )

class _BaseAccessRuleView(ui.View):
    def __init__(
        self, 
        base_view: AccessRuleView,
    ) -> None:
        super().__init__()
        self.base_view = base_view
    
    async def get_content(self) -> str:
        return await self.base_view.get_content()

    async def refresh(self, interaction: Interaction) -> None:
        content = await self.get_content()
        await interaction.response.edit_message(
            content=content,
            view=self,
        )
    
    async def button_cancel_callback(self, interaction: Interaction) -> None:
        self.stop()

        await self.base_view.refresh(interaction)
    
    async def on_error(self, interaction: Interaction, error: Exception, item: Item[Any]) -> None:
        print(traceback.format_exc())

class AccessRuleViewAdd(_BaseAccessRuleView):
    def __init__(
        self, 
        base_view: AccessRuleView,
        ):
        super().__init__(base_view=base_view)
        
        self.accessible_list = self.base_view.accessible_list

        self.rules: List[AbstractAccessRule] = None

        self.items = {
            "select_type": ui.Select(
                placeholder=_("Entities will have access to it or not?"),
                options=[
                    SelectOption(
                        label=_("Have access"),
                        value="True",
                        emoji="✅"
                    ),
                    SelectOption(
                        label=_("Do not have access"),
                        value="False",
                        emoji="❌"
                    ),
                ],
                row=0
            ),
            "selects_entity": [],
            "button_confirm": ui.Button(
                emoji="✅",
                label=_("Confirm"),
                style=ButtonStyle.green,
                disabled=True,
                row=4,
            ),
            "button_cancel": ui.Button(
                emoji="❌",
                label=_("Cancel"),
                style=ButtonStyle.red,
                row=4,
            ),
        }
    
        self.items["select_type"].callback = self.select_type_callback
        self.items["button_confirm"].callback = self.button_confirm_callback
        self.items["button_cancel"].callback = self.button_cancel_callback
        
        if self.base_view.value:
            roles_with_rule = [
                rule.access for rule in self.base_view.value
            ]
        else:
            roles_with_rule = []
        
        self.choices = [
            Choice(
                label=role[0],
                value=role[1],
            ) for role in self.accessible_list
            if not role[1] in roles_with_rule
        ]

        self.choices_map = {
            choice.discord_value: choice.value for choice in self.choices
        }

        self.add_item(self.items["select_type"])

        self.add_item(self.items["button_confirm"])

        self.add_item(self.items["button_cancel"])

    async def add_rule(self, interaction: Interaction) -> None:
        if not self.choices:
            await interaction.response.send_message(
                content=_("There are no roles with no access rule yet."),
                ephemeral=True
            )
            return

        await self.refresh(interaction)

    async def select_type_callback(self, interaction: Interaction) -> None:
        self.items["button_confirm"].disabled = True

        for item in self.items["selects_entity"]:
            self.remove_item(item)


        self.type = self.items["select_type"].values[0]
        
        for option in self.items["select_type"].options:
            if option.value == self.type:
                option.default = True
            else:
                option.default = False
        
        if self.type == "True":
            self.type = True
        else:
            self.type = False

        choices_list = self.choices
        choices_list = split_list(choices_list, 25)

        if len(choices_list) > 3:
            return #todo here
        

        selects_entity = [
            ui.Select(
                placeholder=_("Pick roles in the lists."),
                options=[
                    c.to_select_option() for c in choices
                ],
                max_values=len(choices),
                row=i+1,
            ) for i, choices in enumerate(choices_list)
        ]
        self.items["selects_entity"] = selects_entity

        for select_entity in selects_entity:
            select_entity.callback = self.select_entity_callback
            self.add_item(select_entity)
        
        await self.refresh(interaction)
        
    async def select_entity_callback(self, interaction: Interaction) -> None:
        self.items["button_confirm"].disabled = True

        raw_values = []
        for select in self.items["selects_entity"]:
            raw_values.extend(select.values)


        values = [self.choices_map[raw_value] for raw_value in raw_values]

        self.rules = [
            AbstractAccessRule(access=value, have_access=self.type) for value in values
        ]

        self.items["button_confirm"].disabled = False

        for select in self.items["selects_entity"]:
            for option in select.options:
                if option.value in raw_values:
                    option.default = True
                else:
                    option.default = False

        await self.refresh(interaction)

    async def button_confirm_callback(self, interaction: Interaction) -> None:
        if self.base_view.field.value:
            self.base_view.field.value.extend(self.rules)
        else:
            self.base_view.field.value = self.rules

        self.stop()

        await self.base_view.refresh(interaction)

class AccessRuleViewRemove(_BaseAccessRuleView):
    def __init__(
        self, 
        base_view: AccessRuleView,
    ) -> None:
        super().__init__(base_view=base_view)

        self.guild_id = self.base_view.field.form.guild.id
        
        self.items = {
            "selects_entity": [],
            "button_confirm": ui.Button(
                emoji="✅",
                label=_("Confirm"),
                style=ButtonStyle.green,
                row=4
            ),
            "button_cancel": ui.Button(
                emoji="❌",
                label=_("Cancel"),
                style=ButtonStyle.red,
                row=4
            ),
        }

        self.items["button_confirm"].callback = self.button_confirm_callback
        self.items["button_cancel"].callback = self.button_cancel_callback

        self.add_item(self.items["button_confirm"])
        self.add_item(self.items["button_cancel"])

        self.rules_to_remove: List[AbstractAccessRule] = []
        self.rules: List[AbstractAccessRule] = self.base_view.value

        self.choices: List[Choice] = []
        self.choices_map: Dict[str, AbstractAccessRule] = {}

    async def get_content(self) -> str:
        content = [_("Select the rules you want to remove in the list below.\n\n")]

        for rule in self.rules:
            rule_display = await rule.get_display(guild_id=self.guild_id)

            if rule in self.rules_to_remove:
                content.append("➖ " + rule_display)
            else:
                content.append(rule_display)
        
        return "\n".join(content)

    async def remove_rule(self, interaction: Interaction) -> None:

        rules_map = {rule.access: rule for rule in self.rules}

        accessible_list = self.base_view.accessible_list

        raw_choices = []

        for role in accessible_list:
            if role[1] in rules_map:
                rule = rules_map[role[1]]
                raw_choices.append([role[0], rule])

        self.choices = [
            Choice(
                label=c[0],
                value=c[1],
                emoji="✅" if c[1].have_access else "❌"
            ) for c in raw_choices
        ]

        self.choices_map = {
            c.discord_value:c.value for c in self.choices
        }

        choice_lists = split_list(self.choices, 25)

        if len(choice_lists) > 4:
            return #todo here

        selects_entity = [
            ui.Select(
                placeholder=_("Select rules to remove in the list"),
                options=[c.to_select_option() for c in choices],
                row=i,
                max_values=len(choices),
            ) for i, choices in enumerate(choice_lists)
        ]
        for select in selects_entity:
            select.callback = self.select_entity_callback
            self.add_item(select)
        
        self.items["selects_entity"] = selects_entity

        await self.refresh(interaction)
    
    async def select_entity_callback(self, interaction: Interaction) -> None:

        values = []
        for select in self.items["selects_entity"]:
            values.extend(select.values)
        
        values = [self.choices_map[v] for v in values]

        self.rules_to_remove = values

        await self.refresh(interaction)
        
    async def button_confirm_callback(self, interaction: Interaction) -> None:
        self.base_view.field.value = [
            rule for rule in self.rules if rule not in self.rules_to_remove
        ]
        self.stop()

        await self.base_view.refresh(interaction)
    
class AccessRule(Field):
    def __init__(
        self, 
        name: str, 
        label: str, 
        required: bool = False, 
        validators: List[Callable[[str], bool]] = [], 
        appear_validators: List[Callable[[str], bool]] = [], 
        default: Optional[List[AbstractAccessRule]] = None, 
        **kwargs) -> None:
        super().__init__(
            name, 
            label, 
            required, 
            validators, 
            appear_validators, 
            default, 
            **kwargs
        )
        self.value = default or []

        self.accessible_list: AccessibleList
    
    async def get_accessible_list(self, interaction: Interaction) -> None:
        cluster = await self.get_cluster(interaction)

        roles = await cluster.get_roles_by_name(interaction.client)
        roles = [[name, role] for name, role in roles.items()]

        self.accessible_list = roles
        
    async def ask(self, interaction: Interaction) -> Optional[bool]:
        if not hasattr(self, "accessible_list"):
            await self.get_accessible_list(interaction)
        
        if not self.accessible_list and not self.default:
            await interaction.response.send_message(
                content=_("There are no roles configured, so you can't create an access rule."),
                ephemeral=True
            )
            return
        
        view = AccessRuleView(
            field=self,
        )
        
        content = await view.get_content()
        await interaction.response.send_message(
            content=content,
            embed=None,
            view=view,
            ephemeral=True,
        )
        await view.wait()
        
    
    async def display(self) -> str:
        if not self.value:
            self.display_value = _("*Unanswered*")
        else:
            guild_id = self.form.guild.id
            self.display_value = "\n".join([
                await rule.get_display(guild_id=guild_id) 
                for rule in self.value
            ])

            if len(self.display_value) > 1048:
                self.display_value = self.display_value[:1045] + "..."

        return self.display_value
    