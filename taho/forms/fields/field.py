

from __future__ import annotations
from typing import TYPE_CHECKING
from taho.babel import lazy_gettext
from taho.exceptions import ValidationException
from discord.ui import Modal

if TYPE_CHECKING:
    from typing import List, Callable
    from discord import Interaction
    from taho.forms import Form

__all__ = (
    "Field", 
    "FieldModal",
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
    """
    def __init__(
        self,
        name: str,
        label: str,
        required: bool = False,
        validators: List[Callable[[str], bool]] = [],
        appear_validators: List[Callable[[str], bool]] = [],
        is_current: bool = False,
        **kwargs

    ) -> None:
        self.name = name
        self.label = label
        self.required = required
        self.validators = validators
        self.appear_validators = appear_validators
        self.is_current = is_current

        self.value = None
        self.form: Form = None


        self.display_value = lazy_gettext("*Unanswered*")
        self.kwargs = kwargs
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name} {self.is_current}>"

    def __hash__(self) -> int:
        return hash(self.__repr__())
    
    async def ask(self, interaction: Interaction) -> None:
        """|coro|

        Ask the user for the field's value.

        Parameters
        --------
        interaction: :class:`~discord.Interaction`
            The interaction of the user.
        """
        raise NotImplementedError()
    
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
            try:
                await validator(self.value)
            except ValidationException as e:
                self.value = None
                self.value_display = str(e)
                await interaction.response.send_message(str(e), ephemeral=True)
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
    
    def is_finished(self) -> bool:
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
    """
    def __init__(
        self,
        field: Field,
        *, title: str
    ) -> None:
        super().__init__(title=title)

        self.field = field


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
                lazy_gettext(
                    "Successfully set value to: %(value)s", 
                    value=self.field.display_value
                ),
                ephemeral=True
            )

        self.stop() 