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
from gc import is_finalized
from typing import TYPE_CHECKING
import discord
from taho.babel import lazy_gettext

if TYPE_CHECKING:
    from typing import List, Optional, Tuple, Union
    from .fields import Field
    from taho import TahoContext
    import discord


class FormView(discord.ui.View):
    def __init__(self, form: Form):
        super().__init__()

        self.form = form

        self.message = None
        
        self.cancel.label = lazy_gettext("Cancel")
        self.respond.label = lazy_gettext("Respond")
        self.finish.label = lazy_gettext("Finish")

        self.disable_check()
    
    def get_current_field(self) -> Tuple[Field, int]:
        """
        Get the current field and its index.

        Returns
        --------
        field: :class:`~taho.forms.Field`
            The current field.
        index: :class:`int`
            The index of the current field.
        """
        current_field = discord.utils.find(
            lambda f: f.is_current, self.form.fields
            )
        
        return current_field, self.form.fields.index(current_field)

    def get_next_field(self) -> Tuple[Optional[Field], Optional[int]]:
        """
        Get the next field and its index.

        The next field is not necessarily the field after 
        the current field, it is the next field is the form,
        so the field which must appear.

        The returned values are ``none``, ``None`` if 
        the next field is the same as the current one.

        Returns
        --------
        field: Optional[:class:`~taho.forms.Field`]
            The next field.
        index: Optional:class:`int`]
            The index of the next field.
        """
        _, current_index = self.get_current_field()


        if current_index == len(self.form.fields) - 1:
            return None, None

        # Check for every fields after the current one
        # If they must appear, if so, return as the next field
        for i, field in enumerate(self.form.fields[current_index + 1:]):
            # i is the index of the field after the current one (minus 1)
            if field.must_appear():
                return field, current_index + i + 1

        return None, None

    def get_previous_field(self) -> Tuple[Optional[Field], Optional[int]]:
        """
        Get the previous field and its index.

        The previous field is not necessarily the field before
        the current field, it is the previous field is the form,
        so the field which must appear.

        The returned values are ``none``, ``None`` if
        the previous field is the same as the current one.

        Returns
        --------
        field: Optional[:class:`~taho.forms.Field`]
            The previous field.
        index: Optional:class:`int`]
            The index of the previous field.
        """
        _, current_index = self.get_current_field()

        if current_index == 0:
            return None, None

        # Check for every fields before the current one
        # If they must appear, if so, return as the previous field
        for i, field in enumerate(self.form.fields[:current_index - 1]):
            # i is the index of the field before the current one (plus 1)
            if field.must_appear():
                return field, current_index - i - 1

        return None, None

    def disable_check(self) -> None:
        """
        This function check for every items 
        in the view if they need to be disabled.
        """
        _, next_field = self.get_next_field()
        _, previous_field = self.get_previous_field()

        # If no previous field, the previous button is disabled
        if previous_field is None:
            self.previous.disabled = True
        else:
            self.previous.disabled = False
        
        # If no next field, the next button is disabled
        if next_field:
            self.next.disabled = False
        else:
            self.next.disabled = True
        
        # If the form is finished, the finish button is enabled
        if self.form.is_finished():
            self.finish.disabled = False
        else:
            self.finish.disabled = True
    
    async def refresh(self, interaction: discord.Interaction) -> None:
        """|coro|

        Refresh the form.

        This function perform the following actions:
        - Check items to disabled (:func:`.FormView.disable_check`)
        - Generate a new embed (:func:`.FormView.generate_embed`)
        - Send the embed to the channel (or replace the message)

        Parameters
        -----------
        interaction: :class:`discord.Interaction`
            The interaction of the user.
            Used to send the embed
        """
        self.disable_check()
        
        embed = await self.form.generate_embed()

        if interaction.response._responded:
            original = await interaction.original_message()
            await original.edit(embed=embed, view=self)
        else:
            await interaction.response.edit_message(embed=embed, view=self)
        
    async def paginate_right(self, interaction: discord.Interaction) -> None:
        """|coro|

        Paginate to the next field.

        Parameters
        -----------
        interaction: :class:`discord.Interaction`
            The interaction of the user.
            Used to refresh the form.
        """
        next_field, _ = self.get_next_field()
        current_field, _ = self.get_current_field()

        # If there is no next field, do nothing
        if next_field is None:
            return await self.refresh(interaction)

        current_field.is_current = False
        next_field.is_current = True

        await self.refresh(interaction)
    
    async def paginate_left(self, interaction: discord.Interaction) -> None:
        """|coro|

        Paginate to the previous field.

        Parameters
        -----------
        interaction: :class:`discord.Interaction`
            The interaction of the user.
            Used to refresh the form.
        """
        previous_field, _ = self.get_previous_field()
        current_field, _ = self.get_current_field()

        if previous_field is None:
            return await self.refresh(interaction)

        current_field.is_current = False
        previous_field.is_current = True

        await self.refresh(interaction)
            

    @discord.ui.button(
        emoji="⬅",
        style=discord.ButtonStyle.gray,
        row=1
    )
    async def previous(self, interaction: discord.Interaction, _) -> None:
        await self.paginate_left(interaction)
    
    @discord.ui.button(
        label="respond",
        style=discord.ButtonStyle.blurple,
        row=1
    )
    async def respond(self, interaction: discord.Interaction, _) -> None:
        current_field, current_index = self.get_current_field()

        # Ask for the response corresponding to the current field
        await current_field.ask(interaction)

        # If the current field's value is valid
        # And the pagination is not finished
        # And the next field's value is not valid
        # Paginate to the next field
        if current_field.value is not None \
                and current_index < len(self.form.fields) - 1 \
                and self.form.fields[current_index + 1].value is None:
            return await self.paginate_right(interaction)

        await self.refresh(interaction)
    
    
    @discord.ui.button(
        emoji="➡",
        style=discord.ButtonStyle.gray,
        row=1
    )
    async def next(self, interaction: discord.Interaction, _) -> None:
        await self.paginate_right(interaction)
    
    @discord.ui.button(
        label="finish",
        style=discord.ButtonStyle.green,
        row=2
    )
    async def finish(self, interaction: discord.Interaction, _) -> None:
        await self.finish_form(interaction)

        self.stop()
    
    @discord.ui.button(
        label="cancel",
        style=discord.ButtonStyle.red,
        row=2
    )
    async def cancel(self, interaction: discord.Interaction, _) -> None:
        await self.cancel_form(interaction=interaction)

        self.stop()
    
    async def on_timeout(self) -> None:
        await self.cancel_form(message=self.message)
    
    async def finish_form(self,interaction: discord.Interaction) -> None:

        embed = await self.form.generate_embed(finished=True)

        await interaction.response.edit_message(embed=embed, view=None)


    async def cancel_form(self, interaction: discord.Interaction = None, message: discord.Message = None) -> None:
        
        embed = await self.form.generate_embed(canceled=True)

        if interaction:
            await interaction.response.edit_message(embed=embed, view=None)
        elif message:
            await message.edit(embed=embed, view=None)
        
    

class Form:
    """Represents a form.

    A form is a collection of fields used
    to ask the user to fill in some information.

    Attributes
    -----------
    title: :class:`str`
        The title of the form.
        This is the title of the embed.
    fields: List[:class:`~taho.forms.Field`]
        The fields of the form.
    description: Optional[:class:`str`]
        The description of the form.
        Default to:

        .. code-block:: markdown

            Please fill out the form below.
            You can use the buttons below to navigate the form.
            A title with `*` indicates a required field.
    """
    def __init__(self, title: str, fields: List[Field], description: Optional[str] = None) -> None:
        
        self.title = title
        self.fields = fields
        self.description = description

        if not self.description:
            self.description = lazy_gettext(
                """
                Please fill out the form below.
                You can use the buttons below to navigate the form.
                A title with `*` indicates a required field.
                """
                )

        # The current field of the form
        # is the first in the list to start
        self.fields[0].is_current = True

        for field in self.fields:
            field.form = self
        
    async def send(self, ctx: TahoContext) -> None:
        """|coro|
        
        Send the form to the user.

        Parameters
        -----------
        ctx: :class:`~taho.TahoContext`
            The context of the command.
            Used to send the form.
        """
        view = await self.generate_view()
        embed = await self.generate_embed()
        await ctx.send(embed=embed, view=view)
    
    async def generate_embed(self, canceled: bool = False, finished: bool = False) -> discord.Embed:
        """|coro|

        Generate the embed for the form.

        Parameters
        -----------
        canceled: :class:`bool`
            Whether the form is canceled or not.
            If canceled, the embed will be red.
        finished: :class:`bool`
            Whether the form is finished or not.
            If finished, the embed will be green.
        """
        if canceled:
            color = discord.Color.red()
        elif finished:
            color = discord.Color.green()
        else:
            color = discord.Color.blurple()

        embed = discord.Embed(
            title=self.title,
            description=self.description,
            color=color
        )

        for field in self.fields:
            if canceled or finished:
                field.is_current = False
            
            if not field.must_appear():
                continue
            
            name = f"__**{field.label}**__" if field.is_current else field.label
            if field.required: 
                name += " `*`"

            embed.add_field(
                name=name,
                value=field.display_value,
            )

        return embed
    
    async def generate_view(self) -> FormView:
        """|coro|

        Generate the view for the form.
        """
        view = FormView(self)
        return view
    
    def is_finished(self) -> bool:
        """
        Check if the form is finished.

        The form is finished if all required 
        fields are filled.

        If a field is required but must not appear,
        it is not considered as filled.

        Returns
        --------
        :class:`bool`
            Whether the form is finished or not.
        """
        return all(field.is_finished() for field in self.fields)
    
    def to_dict(self) -> dict:
        """
        Convert the form to a dictionary.
        
        Returns
        --------
        :class:`dict`
            The form as a dictionary.

            
        """
        return {
            field.name: field.value for field in self.fields
        }