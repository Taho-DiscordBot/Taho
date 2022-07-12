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
from taho.enums import RoleType
from tortoise.models import Model
from tortoise import fields
from typing import TYPE_CHECKING, AsyncGenerator
from taho.abc import Shortcutable

if TYPE_CHECKING:
    from taho import Bot
    import discord

__all__ = (
    "Role",
    "ServerRole"
)

class Role(Model, Shortcutable):
    """
    Represents a RP Role of a :class:`~taho.database.models.Cluster`.

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
    
        .. collapse:: cluster

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Cluster`
                - :attr:`related_name` ``roles``
            
            Python: :class:`~taho.database.models.Cluster`
        
        .. collapse:: type

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.RoleType`
                - :attr:`default` :attr:`~taho.enums.RoleType.default`
            
            Python: :class:`~taho.enums.RoleType`

    Attributes
    -----------
    id: :class:`int`
        The role's ID.
    cluster: :class:`~taho.database.models.Cluster`
        The cluster the role is in.
    type: :class:`~taho.enums.RoleType`
        The role's type.
    server_roles: List[:class:`.ServerRole`]
        |coro_attr|

        The role's server roles.
    """
    class Meta:
        table = "roles"

    id = fields.IntField(pk=True)

    cluster = fields.ForeignKeyField("main.Cluster", related_name="roles")
    type = fields.IntEnumField(RoleType, default=RoleType.default)

    server_roles: fields.ReverseRelation["ServerRole"]

    async def get_discord_roles(self, bot: Bot) -> AsyncGenerator[discord.Role]:
        """|coro|

        Get the Discord roles in every guild of the cluster
        for the role.

        Parameters
        -----------
        bot: :class:`~taho.Bot`
            The bot instance.
        
        Returns
        --------
        AsyncGenerator[:class:`discord.Role`]
            The Discord roles.
        """
        # Go through all guilds
        async for s_role in self.server_roles.prefetch_related("server"):
            # Get the role from the Server object
            yield await s_role.server.get_role(bot, s_role.discord_role_id)

class ServerRole(Model):
    """
    Represents a RP role in a :class:`~taho.database.models.Server`.

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
        
        .. collapse:: role

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Role`
                - :attr:`related_name` ``server_roles``
            
            Python: :class:`~taho.database.models.Role`
        
        .. collapse:: server

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Server`
                - :attr:`related_name` ``roles``
            
            Python: :class:`~taho.database.models.Server`
        
        .. collapse:: discord_role_id

            Tortoise: :class:`tortoise.fields.BigIntField`

            Python: :class:`int`
    
    Attributes
    -----------
    id: :class:`int`
        The role's ID.
    role: :class:`~taho.database.models.Role`
        The role of the cluster.
    server: :class:`~taho.database.models.Server`
        The server the role is in.
    discord_role_id: :class:`int`
        The Discord role's ID.
    """
    class Meta:
        table = "server_roles"

    id = fields.IntField(pk=True)

    role = fields.ForeignKeyField("main.Role", related_name="server_roles")
    server = fields.ForeignKeyField("main.Server", related_name="server_roles")
    discord_role_id = fields.BigIntField()

    @property
    def d_role_id(self) -> int:
        """
        :class:`int`: Shortcut for :attr:`.discord_role_id`.
        """
        return self.discord_role_id

    async def discord_role(self, bot: Bot) -> discord.Role:
        """
        Get the :class:`discord.Role` object for this role in the guild.

        Parameters
        -----------
        bot: :class:`~taho.Bot`
            The bot instance.
        
        Returns
        --------
        :class:`discord.Role`
            The Discord role.
        """
        server = await self.server
        return  await server.get_role(bot, self.discord_role_id)