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
from tortoise.models import Model
from tortoise import fields
from tortoise.signals import post_save

if TYPE_CHECKING:
    from typing import List
    from .user import User
    from .role import Role

__all__ = (
    "NPC",
    "NPCOwner",
    "NPCRole",
    "NPCMessage",
)

class NPC(Model):
    """Represents a NPC.

    .. container:: operations

        .. describe:: x == y

            Checks if two NPCs are equal.

        .. describe:: x != y

            Checks if two NPCs are not equal.
        
        .. describe:: hash(x)

            Returns the npc's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: cluster

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Cluster`
                - :attr:`related_name` ``npcs``
            
            Python: :class:`~taho.database.models.Cluster`
        
        .. collapse:: name

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
            
            Python: :class:`str`
        
        .. collapse:: avatar

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
                - :attr:`null` ``True``
            
            Python: Optional[:class:`str`]
        
        .. collapse:: description

            Tortoise: :class:`tortoise.fields.TextField`

                - :attr:`null` ``True``
            
            Python: Optional[:class:`str`]
        
    Attributes
    -----------
    id: :class:`int`
        The NPC's ID.
    cluster: :class:`~taho.database.models.Cluster`
        The cluster the NPC belongs to.
    name: :class:`str`
        The NPC's name.
    avatar: Optional[:class:`str`]  
        The NPC's avatar (url).
    description: Optional[:class:`str`]
        The NPC's description.
    roles: List[:class:`~taho.database.models.NPCRole`]
        |coro_attr|

        The roles the NPC has.
    users: List[:class:`~taho.database.models.NPCOwner`]
        |coro_attr|

        The users who own the NPC.
    messages: List[:class:`~taho.database.models.NPCMessage`]
        |coro_attr|

        The messages sent by the NPC.
    """
    class Meta:
        table = "npcs"

    id = fields.IntField(pk=True)
    cluster = fields.ForeignKeyField("main.Cluster", related_name="npcs")
    name = fields.CharField(max_length=255)
    avatar = fields.CharField(max_length=255, null=True)
    description = fields.TextField(null=True)

    users: fields.ReverseRelation["NPCOwner"]
    roles: fields.ReverseRelation["NPCRole"]
    messages: fields.ReverseRelation["NPCMessage"]

    async def add_roles(self, *roles: List[Role]) -> None:
        """|coro|

        Add roles to the NPC.

        Parameters
        -----------
        roles: List[:class:`~taho.database.models.Role`]
            The roles to add.
        """
        await NPCRole.filter(npc=self, role__in=roles).delete()
        await NPCRole.bulk_create([NPCRole(npc=self, role=r) for r in roles])

    async def remove_roles(self, *roles: List[Role]) -> None:
        """|coro|

        Remove roles from the NPC.

        Parameters
        -----------
        roles: List[:class:`~taho.database.models.Role`]
            The roles to remove.
        """
        await NPCRole.filter(npc=self, role__in=roles).delete()

    async def get_user(self) -> User:
        """|coro|
        
        Get the :class:`~taho.database.models.User` that 
        represents the NPC.

        Returns
        --------
        :class:`~taho.database.models.User`
            The user.
        """
        from .user import User # Avoid circular import
        return (await User.get_or_create(user_id=self.id, cluster=self.cluster))[0]

    async def get_users(self) -> List[NPCOwner]:
        """|coro|

        Get all the users who own the NPC.

        Returns
        --------
        List[:class:`~taho.database.models.NPCOwner`]
            The users.
        

        .. note::

            :class:`~taho.database.models.NPCOwner` is different from
            :class:`~taho.database.models.User`.

        """
        return [await u.user async for u in self.users]
        
@post_save(NPC)
async def on_npc_save(_, instance: NPC, created: bool, *args, **kwargs) -> None:
    if created:
        from .user import User # circular import
        await User.get_or_create(user_id=instance.id, cluster=instance.cluster)

class NPCOwner(Model):
    """Represents an owner of a NPC.

    .. container:: operations

        .. describe:: x == y

            Checks if two owners are equal.

        .. describe:: x != y

            Checks if two owners are not equal.
        
        .. describe:: hash(x)

            Returns the owner's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: npc

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.NPC`
                - :attr:`related_name` ``users``
            
            Python: :class:`~taho.database.models.NPC`
        
        .. collapse:: user

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.User`
                - :attr:`related_name` ``npcs``
            
            Python: :class:`~taho.database.models.User`
        
        .. collapse:: original_owner

            Tortoise: :class:`tortoise.fields.BooleanField`

                - :attr:`default` ``False``
            
            Python: :class:`bool`
        
        .. collapse:: pattern

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
                - :attr:`null` ``True``
            
            Python: Optional[:class:`str`]
        
        .. collapse:: is_selected

            Tortoise: :class:`tortoise.fields.BooleanField`

                - :attr:`default` ``False``
            
            Python: :class:`bool`

    Attributes
    -----------
    id: :class:`int`
        The owner's ID.
    npc: :class:`~taho.database.models.NPC`
        The NPC that the owner owns.
    user: :class:`~taho.database.models.User`
        The user that owns the NPC.
    original_owner: :class:`bool`
        Whether the user is the original owner of the NPC.
    pattern: Optional[:class:`str`]
        The pattern used to send RP messages in a RP channel.
    is_selected: :class:`bool`
        Whether the user has selected the NPC.
    """
    class Meta:
        table = "npc_owners"

    id = fields.IntField(pk=True)

    npc = fields.ForeignKeyField("main.NPC", related_name="users")
    user = fields.ForeignKeyField("main.User", related_name="npcs")
    original_owner = fields.BooleanField(default=False)
    pattern = fields.CharField(max_length=255, null=True)
    is_selected = fields.BooleanField(default=False)

    def __repr__(self) -> str:
        return super().__repr__()
    
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)
    
    def __ne__(self, other: object) -> bool:
        return not super().__eq__(other)
    
    def __hash__(self) -> int:
        return hash(self.__repr__())

class NPCRole(Model):
    """Represents a role of a NPC.

    .. container:: operations

        .. describe:: x == y

            Checks if two roles are equal.

        .. describe:: x != y

            Checks if two roles are not equal.
        
        .. describe:: hash(x)

            Returns the role's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: npc

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.NPC`
                - :attr:`related_name` ``roles``
            
            Python: :class:`~taho.database.models.NPC`
        
        .. collapse:: role

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Role`
                - :attr:`related_name` ``npcs``
            
            Python: :class:`~taho.database.models.Role`

    Attributes
    -----------
    id: :class:`int`
        The role's ID.
    npc: :class:`~taho.database.models.NPC`
        The NPC that the role belongs to.
    role: :class:`~taho.database.models.Role`
        The role that the NPC belongs to.
    """
    class Meta:
        table = "npc_roles"

    id = fields.IntField(pk=True)

    npc = fields.ForeignKeyField("main.NPC", related_name="roles")
    role = fields.ForeignKeyField("main.Role", related_name="npc_roles")

    def __repr__(self) -> str:
        return super().__repr__()
    
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)
    
    def __ne__(self, other: object) -> bool:
        return not super().__eq__(other)
    
    def __hash__(self) -> int:
        return hash(self.__repr__())

class NPCMessage(Model):
    """Represents a message sent by a NPC.

    .. container:: operations

        .. describe:: x == y

            Checks if two messages are equal.

        .. describe:: x != y

            Checks if two messages are not equal.
        
        .. describe:: hash(x)

            Returns the message's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: npc

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.NPC`
                - :attr:`related_name` ``messages``
            
            Python: :class:`~taho.database.models.NPC`
        
        .. collapse:: channel

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Channel`
                - :attr:`related_name` ``npc_messages``
            
            Python: :class:`~taho.database.models.Channel`
        
        .. collapse:: message_id

            Tortoise: :class:`tortoise.fields.BigIntField`

                - :attr:`null` ``True``
            
            Python: Optional[:class:`int`]
        
        .. collapse:: message_type

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
                - :attr:`null` ``True``
            
            Python: Optional[:class:`str`]
        
        .. collapse:: message_content

            Tortoise: :class:`tortoise.fields.TextField`

                - :attr:`null` ``True``
            
            Python: Optional[:class:`str`]
        
        .. collapse:: message_timestamp

            Tortoise: :class:`tortoise.fields.BigIntField`

                - :attr:`null` ``True``
            
            Python: Optional[:class:`int`]
        
        .. collapse:: message_sender

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.User`
                - :attr:`related_name` ``npc_messages``
            
            Python: :class:`~taho.database.models.User`
        
        .. collapse:: message_sender_name

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
                - :attr:`null` ``True``
            
            Python: Optional[:class:`str`]
        
        .. collapse:: message_sender_role

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Role`
                - :attr:`related_name` ``npc_messages``
            
            Python: :class:`~taho.database.models.Role`
        
        .. collapse:: message_sender_role_name

            Tortoise: :class:`tortoise.fields`

                - :attr:`null` ``True``
            
            Python: Optional[:class:`str`]
        
        .. collapse:: timestamp

            Tortoise: :class:`tortoise.fields.DatetimeField`

                - :attr:`auto_now_add` ``True``
            
            Python: :class:`datetime.datetime`

    Attributes
    -----------
    id: :class:`int`
        The message's ID.
    npc: :class:`~taho.database.models.NPC`
        The NPC that sent the message.
    channel: :class:`~taho.database.models.Channel`
        The channel that the message was sent in.
    message: Optional[:class:`str`]
        The message that was sent.
    timestamp: :class:`datetime.datetime`
        The timestamp of the message.
    """
    class Meta:
        table = "npc_messages"

    id = fields.IntField(pk=True)

    npc = fields.ForeignKeyField("main.NPC", related_name="messages")
    channel = fields.ForeignKeyField("main.ServerChannel", related_name="npc_messages")
    message = fields.TextField(null=True)
    timestamp = fields.DatetimeField(auto_now_add=True)

    def __repr__(self) -> str:
        return super().__repr__()
    
    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)
    
    def __ne__(self, other: object) -> bool:
        return not super().__eq__(other)
    
    def __hash__(self) -> int:
        return hash(self.__repr__())
