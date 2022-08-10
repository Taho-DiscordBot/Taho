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
from taho.babel import _
from taho.exceptions import ValidationException
from discord.ui import Modal, View
from discord import AllowedMentions
from taho.database import utils as db_utils

if TYPE_CHECKING:
    from typing import List, Callable, Optional, TypeVar
    from discord import Interaction
    from taho.forms import Form
    from taho.database.models import Cluster

    T = TypeVar('T')

__all__ = (
    "Field", 
    "FieldModal",
    "FieldView",
)

class Field:
    """Represent a field in a :class:`~taho.forms.Form`.

    Attributes
    -----------
    name: :class:`str`
        The name of the field.
        Used to identify the field in the form.
    label: :class:`str`
        The label of the field.
        Used to display the field in the form.
    required: :class:`bool`
        Whether the field is required.
        If the field is required, don't forget
        to add the validator :class:`~taho.forms.validators.required`
        in ``validators``.
    validators: List[:class:`callable`]
        The list of validators of the field.
        A validator must meet the following format:

        .. code-block:: python3

            lambda x: validator(x)
        
        In the code, ``validator`` is a function from
        :module:`taho.forms.validators`.
    appear_validators: List[:class:`callable`]
        The list of validators of the field.
        A validator must meet the following format:

        .. code-block:: python3

            lambda f: ...
        
        In the code, ``f`` is the form's dictionary
        from :class:`~taho.forms.Form.to_dict`.
    is_current: :class:`bool`
        Whether the field is the current field.

        In general, keep it to ``False`` when
        creating a field.
    default: Optional[:class:`str`]
        The default value of the field.
    """
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
        self.name = name
        self.label = label
        self.required = required
        self.validators = validators
        self.appear_validators = appear_validators
        self.default = default

        self.is_current = False
        self.value = None
        self.form: Form = None


        self.display_value = _("*Unanswered*")
        self.kwargs = kwargs
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name} {self.is_current}>"

    def __hash__(self) -> int:
        return hash(self.__repr__())
    
    async def get_cluster(self, interaction: Interaction) -> Cluster:
        """|coro|

        Get the cluster corresponding of the guild where 
        the field's form is displayed.

        Parameters
        -----------
        interaction: :class:`~discord.Interaction`
            The interaction of the user.
        
        Returns
        --------
        :class:`~taho.database.models.Cluster`
            The cluster.
        """
        if hasattr(self, "cluster"):
            return self.cluster
        else:
            self.cluster = await db_utils.get_cluster(
                interaction.client,
                interaction.guild
            )
            return self.cluster
    
    async def ask(self, interaction: Interaction) -> Optional[bool]:
        """|coro|

        Ask the user for the field's value.

        Parameters
        --------
        interaction: :class:`~discord.Interaction`
            The interaction of the user.
        
        Returns
        --------
        Optional[:class:`bool`]
            Whether the form can be refreshed.
            If ``None``, the form can be refreshed.
        """
        raise NotImplementedError()
    
    async def _validate(self, interaction: Interaction, *validators: Callable[[str], bool]) -> bool:
        """|coro|

        Validate the field's value.
        
        This function calls the ``validator``.
        If the validator fails, the field is invalid and
        an error message is displayed to the user.

        Parameters
        -----------
        interaction: :class:`~discord.Interaction`
            The interaction of the user.
        validator: :class:`callable`
            The validator of the field.
        
        Returns
        --------
        :class:`bool`
            Whether the field is valid.
        """
        for validator in validators:
            try:
                await validator(self.value)
            except ValidationException as e:
                self.value = None
                self.value_display = str(e)
                params = {
                    "content": str(e),
                    "ephemeral": True,
                }
                if interaction.response.is_done():
                    await interaction.followup.send(**params)
                else:
                    await interaction.response.send_message(**params)
                return False
        return True

    async def validate(self, interaction: Interaction) -> bool:
        """|coro|

        Validate the field's value.
        
        This function calls the ``validators`` of the field.
        If one of the validators fails, the field is invalid and
        an error message is displayed to the user.

        Parameters
        -----------
        interaction: :class:`~discord.Interaction`
            The interaction of the user.
        
        Returns
        --------
        :class:`bool`
            Whether the field is valid.
        """
        for validator in self.validators:
            valid = await self._validate(interaction, validator)
            if not valid:
                return False
        return True
    
    def must_appear(self) -> bool:
        """|coro|

        Check if the field must appear in the form.

        This function calls the ``appear_validators`` of the field.

        Returns
        --------
        :class:`bool`
            Whether the field must appear in the form.
        """
        for validator in self.appear_validators:
            if not validator(self.form.to_dict()):
                return False

        return True
    
    def is_completed(self) -> bool:
        """
        Check if the field is finished.

        A field is finished when:
        - it's required and filled
        - it's not required
        - it must not appear in the form

        Returns
        --------
        :class:`bool`
            Whether the field is finished.
        """
        return (self.required and self.value is not None) \
                or not self.required \
                or not self.must_appear()
    
    async def display(self) -> str:
        """|coro|

        Generate and return the display value of the field.

        Returns
        --------
        :class:`str`
            The display value of the field.
        """
        raise NotImplementedError()

class FieldModal(Modal):
    """The default modal for any field.
    
    Attributes
    -----------
    field: :class:`~taho.forms.Field`
        The field corresponding to the modal.
    title: :class:`str`
        The title of the modal.
    default:
        The default value of the field.
    """
    def __init__(
        self,
        field: Field,
        *, title: str,
        default: Optional[T] = None,
    ) -> None:
        super().__init__(title=title)

        self.field = field
        self.default = default

    async def on_submit(self, interaction: Interaction) -> None:
        """|coro|

        Called when the user submit the modal.

        This function performs the following actions:
        - check if the field is valid using :meth:`~taho.forms.Field.validate`
        - get the display value of the field using :meth:`~taho.forms.Field.display`
        - send a message to the user with the display value, if the field is valid
        """
        is_valid = await self.field.validate(interaction)

        await self.field.display()

        if is_valid:
            await interaction.response.send_message(
                _(
                    "Successfully set value to: %(value)s", 
                    value=self.field.display_value
                ),
                ephemeral=True,
                allowed_mentions=AllowedMentions.none()
            )

        self.stop() 

class FieldView(View):
    """The default view for any field.
    
    Attributes
    -----------
    field: :class:`~taho.forms.Field`
        The field corresponding to the view.
    default:
        The default value of the field.
    """
    def __init__(
        self,
        field: Field,
        default: Optional[T] = None,
    ) -> None:
        super().__init__()

        self.field = field
        self.default = default

    async def on_submit(self, interaction: Interaction) -> None:
        """|coro|

        Called when the user submit the view.

        This function performs the following actions:
        - check if the field is valid using :meth:`~taho.forms.Field.validate`
        - get the display value of the field using :meth:`~taho.forms.Field.display`
        - send a message to the user with the display value, if the field is valid
        """
        is_valid = await self.field.validate(interaction)

        await self.field.display()

        if is_valid:
            params = {
                "content": _(
                    "Successfully set value to: %(value)s", 
                    value=self.field.display_value
                ),
                "ephemeral": True,
                "allowed_mentions": AllowedMentions.none()
            }
            if interaction.response.is_done():
                await interaction.followup.send(**params)
            else:
                await interaction.response.send_message(**params)

        self.stop() 
