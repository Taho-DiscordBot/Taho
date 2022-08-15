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
from itertools import chain
from typing import TYPE_CHECKING
from tortoise.models import Model
from taho.abc import Shortcutable
from taho.enums import ShortcutType
from taho.emoji import Emoji
import asyncio

if TYPE_CHECKING:
    from typing import Optional, Iterable, List, Any, Type, TypeVar
    from tortoise import BaseDBAsyncClient

    MODEL = TypeVar('MODEL', bound="BaseModel")

    __all__ = (
        "BaseModel",
        "MODEL",
    )

else:

    __all__ = (
        "BaseModel",
    )

# This class is used to avoid reusing the same coroutine
# multiple times (which results in a RuntimeError).
class _Shortcut:
    def __init__(self, model: BaseModel, field_name: str):
        self.model = model
        self.field_name = field_name
    
    def __await__(self):
        from taho.database.utils import get_shortcut

        # The get_shortcut function is a coroutine,
        # it will cache the shortcut model to avoid 
        # multi-time fetching.
        return get_shortcut(self.model, self.field_name).__await__()

class BaseModel(Model):
    class Meta:
        abstract = True
    
    @classmethod
    def get_fields(cls) -> List[dict]:
        desc = cls.describe(serializable=True)
        return [
            field
            for field in chain(
                desc.get("data_fields", []),
                desc.get("fk_fields", []),
                desc.get("o2o_fields", []),
            )
        ]
    
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)
    
    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)
    
    def __repr__(self) -> str:
        return super().__repr__()
    
    def __hash__(self) -> int:
        return hash(self.__repr__())
    
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        for key in kwargs:
            if not hasattr(self, key):
                setattr(self, key, kwargs[key])
        
        if hasattr(self, "emoji") and self.emoji and not isinstance(self.emoji, Emoji):
            self.emoji = Emoji(self.emoji)
    
    async def save(
        self,
        using_db: Optional[BaseDBAsyncClient] = None,
        update_fields: Optional[Iterable[str]] = None,
        force_create: bool = False,
        force_update: bool = False,
    ) -> None:

        if hasattr(self, "emoji") and self.emoji:
            emoji = self.emoji
            self.emoji = self.emoji.to_db_value()

        from ..utils import create_shortcut

        # Here, the goal is to set the shortcuts fields of 
        # the model, from the properties of the model.

        # Example, we are creating a Model with a 
        # "owner_shortcut" field, which is not filled.
        # Instead, we have a "owner" property, which points
        # to a Shortcutable model, but not a Shortcut model.
        # So we are going to create a shortcut from the
        # owner property.

        tasks = []

        async def register_shortcut(
            type_: ShortcutType, 
            model: Shortcutable, 
            field_name: str
            ) -> None:
            id_name = field_name + "_id"

            short_name = field_name.replace("_shortcut", "")

            shortcut = await create_shortcut(type_, model)

            # Field the shortcut field.
            setattr(self, id_name, shortcut.id)

            # Set attributes to correspond with the system
            # in _init_from_db.

            # The attribute with the model is changed to
            # a coroutine, so we can use it in the future.
            # This coroutine will directly return the model
            # from the cache.
            setattr(self, short_name, _Shortcut(self, field_name))

            # The model is cached under a different name.
            setattr(self, "_"+short_name, model)

        for field in self.get_fields():
            field_name = field.get("name", "")

            # Check if the field is a shortcut field.
            if "shortcut" in field_name:
                id_name = field_name + "_id"
                short_name = field_name.replace("_shortcut", "")
                
                # Check if the supposed shortcut field is a shortcut field,
                # and if the property is defined.
                if hasattr(self, id_name) and hasattr(self, short_name):

                    # Get the property.
                    shortcut_model = getattr(self, short_name)

                    # Get the ShortcutType of the model, to get 
                    # the corresponding Shortcut model.
                    shortcut_type = field.get("python_type", "").replace("main.", "")
                    shortcut_type = ShortcutType(shortcut_type)

                    # Create the shortcut and set the shortcut field.
                    tasks.append(register_shortcut(shortcut_type, shortcut_model, field_name))

        # Wait for all the tasks to finish.
        await asyncio.wait_for(
            asyncio.gather(*tasks),
            timeout=None,
        )

        await super().save(
            using_db=using_db,
            update_fields=update_fields,
            force_create=force_create,
            force_update=force_update,
        )

        if hasattr(self, "emoji") and self.emoji:
            self.emoji = emoji
    
    @classmethod
    def _init_from_db(cls: Type[MODEL], **kwargs: Any) -> MODEL:
        model = super()._init_from_db(**kwargs)

        # Here we want to register a coroutine to get the models
        # pointed to by the shortcuts.
        # This will avoid double awaiting the shortcuts.
        # Because when we have a field that is a shortcut,
        # we have to await it a first time to get the Shortcut,
        # and a second time to get the model (Shortcutable).

        for field in model.get_fields():
            field_name = field.get("name", "")

            # If the field is a shortcut (contains "_shortcut")
            # in the name, we want to register a coroutine.
            if "shortcut" in field_name:
                id_name = field_name + "_id"
                short_name = field_name.replace("_shortcut", "")

                # If the model already has the coroutine registered,
                # we don't want to register it again.
                if hasattr(model, id_name) and not hasattr(model, short_name):
                    
                    # Register the coroutine.
                    setattr(model, short_name, _Shortcut(model, field_name))
        

        if hasattr(model, "emoji") and model.emoji:
            model.emoji = Emoji(model.emoji)
        # Example:
        # The model which is initialized from the database
        # has a field called "owner_shortcut".
        # We are going to check if a "owner" property exists
        # in the model.
        # If it does not, we want to register a coroutine
        # to get the model pointed to by the shortcut.
        # So if we do "await model.owner", we will get the
        # model pointed to by the shortcut directly.
        
        return model