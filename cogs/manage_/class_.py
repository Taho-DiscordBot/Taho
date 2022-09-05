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
import discord
from discord import SelectOption
from discord.app_commands import Choice
from discord.ui import Select
from taho import forms, utils, _, views, ngettext, BaseView
from taho.database import Class

if TYPE_CHECKING:
    from typing import List, Literal, Optional
    from taho import Bot, TahoContext
    from discord.abc import Snowflake

__all__ = (
    "ManageClass",
)

class ClassActionChoiceView(BaseView):
    def __init__(self, user: Optional[Snowflake] = None, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

        self.value: Literal["create", "delete", "edit", "list"] = None

        actions = {
            "create": _("Create a class"),
            "edit": _("Edit an existing class"),
            "delete": _("Delete an existing class"),
            "list": _("List all classes"),
        }

        self.select = Select(
            placeholder=_("Select an action"),
            options=[
                SelectOption(
                    label=label,
                    value=value
                ) for value, label in actions.classes()
            ]
        )
        self.add_item(self.select)
        self.select.callback = self.select_callback
    
    async def select_callback(self, interaction: discord.Interaction):
        self.value = self.select.values[0]
        await interaction.response.defer(ephemeral=True)
        self.stop()

class ClassChoiceView(BaseView):
    def __init__(self, classes: List[Class], user: Optional[Snowflake] = None, multiple: bool = False):
        super().__init__(user)

        self.value: Class = None
        self.multiple = multiple

        choices = [
            forms.Choice(
                label=class_.name,
                value=class_,
                emoji=class_.emoji
            ) for class_ in classes
        ]

        self.choices_map = {
            choice.discord_value: choice.value for choice in choices
        }

        choices_list = utils.split_list(choices, 25)

        if len(choices_list) > 5:
            return #todo choices_list too long

        self.selects = [
            Select(
                placeholder=_("Select a class"),
                options=choices,
                max_values=1 if not self.multiple else len(choices)
            ) for choices in choices_list
        ]

        for select in self.selects:
            self.add_item(select)
            select.callback = self.select_callback

    
    async def select_callback(self, interaction: discord.Interaction):
        values = []
        for select in self.selects:
            values.extend(select.values)
        
        if len(values) > 1 and not self.multiple:
            await interaction.response.send_message(
                _("Please select only one class_."),
                ephemeral=True
            )
        else:
            if self.multiple:
                self.value = [
                    self.choices_map[value] for value in values
                ]
            else:
                self.value = self.choices_map[values[0]]

            await interaction.response.defer(ephemeral=True)
            self.stop()

class ManageClass:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
    
    async def get_class_form(
        self, 
        ctx: TahoContext, 
        class_: Class=None, 
        class_dict: dict=None,
        is_info: bool=False
        ) -> forms.Form:
        """|coro|
        
        Get a form to create or edit a class.
        The form will be prefilled with the information
        from ``class`` if given.

        Parameters
        -----------
        ctx: :class:`TahoContext`
            The context of the command.
        class_: Optional[:class:`~taho.database.models.Class`]
            The class to prefill the form with.
        class_dict: Optional[:class:`dict`]
            The class to prefill the form with.
        is_info: :class:`bool`
            Whether the form is for info or not.
            If ``True``, the form will not be editable.

            Defaults to ``False``.
        
        Raises
        -------
        TypeError
            If both ``class_`` and ``class_dict`` are given.
            If ``is_info`` is ``True`` and neither ``class_`` nor ``class_dict`` are given.
        
        Returns
        --------
        :class:`~taho.forms.Form`
            The form to create or edit a class.
        """
        if class_ and class_dict:
            raise TypeError("Cannot prefill form with both class_ and class_dict.")
        elif is_info and not (class_ or class_dict):
            raise TypeError("Cannot get info form without class_ or class_dict.")
        cluster = await ctx.get_cluster()
        forbidden_names = await cluster.classes.all().values_list("name", flat=True)

        if class_:
            fields_default = await class_.to_dict()
        elif class_dict:
            fields_default = class_dict
        else:
            fields_default = None

        fields: List[forms.Field] = [
            forms.Text(
                name="name",
                label=_("Name"),
                description=_("The name of the class"),
                required=True,
                max_length=32,
                min_length=3,
                validators=[
                    lambda x: forms.required(x),
                    lambda x: forms.min_length(x, 3),
                    lambda x: forms.max_length(x, 32),
                    lambda x: forms.forbidden_value(x, *forbidden_names),
                ]
            ),
            forms.Emoji(
                name="emoji",
                label=_("Emoji"),
                description=_("The emoji of the class"),
                required=False
            ),
            forms.Text(
                name="description",
                label=_("Description"),
                description=_("The description of the class"),
                required=False,
                validators=[
                    lambda x: forms.min_length(x, 3),
                    lambda x: forms.max_length(x, 100),
                ]
            ),
            forms.Stat(
                name="stats",
                label=_("Stats"),
                description=_("The stats of the class"),
                required=False,
            )
        ]
        if fields_default:
            if is_info:
                form_title = fields_default["name"]
            else:
                form_title = _("Edit %(class_name)s", class_name=fields_default["name"])


            for field in fields:
                await field.set_value(fields_default.get(field.name, None))
        else:
            form_title = _("Create a class")
    
        form = forms.Form(
            title=form_title,
            fields=fields,
            is_info=is_info,
        )
        return form

    async def callback(self, ctx: TahoContext, action: Choice[str] = None):
        if not action:
            view = ClassActionChoiceView(user=ctx.author)
            await ctx.send(view=view)
            await view.wait(delete_after=True)

            if view.value is None:
                return
            
            action = view.value
        
        cluster = await ctx.get_cluster()

        if action == "create":
            
            form = await self.get_class_form(ctx)
                
            await form.send(ctx=ctx)

            await form.wait()

            if form.is_canceled():
                return

            class_ = await cluster.create_class(**form.to_dict())
        
            await ctx.send(
                content=_(
                "You have successfully created the class **%(class_display)s**.",
                class_display=str(class_)
                ),
                ephemeral=True
            )

        elif action == "edit":
            classes = await cluster.classes.all()

            if not classes:
                await ctx.send(
                    _("There are no classes to edit."),
                    ephemeral=True
                )
                return
            
            view = ClassChoiceView(classes, user=ctx.author)
            await ctx.send(view=view)

            await view.wait(delete_after=True)
            class_ = view.value

            if not class_:
                return
            
            class_dict = await class_.to_dict(to_edit=True)
            
            form = await self.get_class_form(ctx, class_dict=class_dict)
            await form.send(ctx=ctx)
            await form.wait()

            if form.is_canceled():
                return

            await class_.edit(**form.to_dict())
        
            await ctx.send(
                content=_(
                    "You have successfully edited the class **%(class_display)s**.",
                    class_display=str(class_)
                ),
                ephemeral=True
            )

        elif action == "delete":
            classes = await cluster.classes.all()

            if not classes:
                await ctx.send(
                    _("There are no classes to delete."),
                    ephemeral=True
                )
                return
            
            view = ClassChoiceView(classes, user=ctx.author, multiple=True)
            await ctx.send(view=view)

            await view.wait(delete_after=True)
            classes = view.value

            if not classes:
                return
            
            classes_display = ", ".join(str(class_) for class_ in classes) if len(classes) > 1\
                else str(classes[0])
            
            confirmation = views.ConfirmationView(user=ctx.author)
            msg = await ctx.send(
                ngettext(
                    "Are you sure you want to delete the class **%(class_)s**?",
                    "Are you sure you want to delete the classes **%(class_)s**?",
                    num=len(classes),
                    class_=classes_display
                ),
                view=confirmation
                )

            await confirmation.wait()
            await msg.delete(delay=0)
            if confirmation.value is False:
                return
            
            await Class.filter(id__in=[class_.id for class_ in classes]).delete()
            
            await ctx.send(
                ngettext(
                    "You have successfully deleted the class **%(class_)s**.",
                    "You have successfully deleted the classes **%(class_)s**.",
                    num=len(classes),
                    class_=classes_display
                ),
                ephemeral=True
            )

        elif action == "list":
            classes = await cluster.classes.all()

            if not classes:
                await ctx.send(
                    _("There are no classes to list."),
                    ephemeral=True
                )
                return

            content = _(
                "Here is a list of all classes, select a class in the selects "
                "below to get more information about it.\n\n"
                "%(classes)s",
                classes="\n".join(class_.get_display(long=True) for class_ in classes)
            )
            view = ClassChoiceView(classes, user=ctx.author)
            msg = await ctx.send(content=content, view=view)

            await view.wait()

            class_ = view.value

            if not class_:
                await msg.edit(view=None)
                return
            
            await msg.delete(delay=0)

            class_dict = await class_.to_dict()

            form = await self.get_class_form(ctx, class_dict=class_dict, is_info=True)

            await form.send(ctx=ctx, ephemeral=True)
