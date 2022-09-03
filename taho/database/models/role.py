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
from .base import BaseModel
from tortoise import fields
from typing import TYPE_CHECKING
from taho.enums import RoleType
from taho.abc import AccessRuleShortcutable, StuffShortcutable
from taho.exceptions import DoesNotExist
from .. import db_utils


if TYPE_CHECKING:
    from taho import Bot
    import discord
    from typing import Optional, List

__all__ = (
    "Role",
    "ServerRole"
)

class Role(BaseModel, StuffShortcutable, AccessRuleShortcutable):
    """|shortcutable|
    
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

    async def get_discord_roles(self, bot: Bot) -> List[discord.Role]:
        """|coro|

        Get the Discord roles in every guild of the cluster
        for the role.

        Parameters
        -----------
        bot: :class:`~taho.Bot`
            The bot instance.
        
        Returns
        --------
        List[:class:`discord.Role`]
            The Discord roles.
        """
        server_roles = await self.server_roles.all()
        return [
            db_utils.get_discord_role(bot, s_role.server_id, s_role.discord_role_id)
            for s_role in server_roles
        ]
        return roles

    async def get_discord_role(self, bot: Bot, server_id: int) -> discord.Role:
        """|coro|

        Get the Discord role in the server with the given ID.
        
        Parameters
        -----------
        bot: :class:`~taho.Bot`
            The bot instance.
        server_id: :class:`int`
            The server ID.
        
        Returns
        --------
        Optional[:class:`discord.Role`]
            The Discord role.
        
        Raises
        -------
        ~taho.exceptions.DoesNotExist
            If the role does not exist in the server.
        """
        server_role = await self.server_roles.filter(server_id=server_id).first()
        if not server_role:
            raise DoesNotExist(f"Role {self.id} does not exist in server {server_id}")
        return await server_role.get_role(bot)

    async def add_roles(self, *roles: discord.Role, return_roles: bool = False) -> Optional[List[ServerRole]]:
        """|coro|

        Create a :class:`.ServerRole` for each role 
        and add it to the database.

        Parameters
        -----------
        roles: List[:class:`discord.Role`]
            The roles to add.
        return_roles: :class:`bool`
            Whether to return the created roles.
        
        Returns
        --------
        Optional[List[:class:`.ServerRole`]]
            The created roles.
            Only if ``return_roles`` is ``True``.
        

        .. note::

            Set ``return_roles`` to ``True`` will create a query
            for each role, which will be slower.
        """
        models = []
        for role in roles:
            models.append(ServerRole(
                server_id=role.guild.id,
                discord_role_id=role.id,
                role=self
            ))
        if return_roles:
            for model in models:
                await model.save()
            return models
        else:
            await ServerRole.bulk_create(models)

    async def get_display(self, bot: Bot, server_id: int = None) -> str:
        """|coro|

        Get the display name of the role.
        
        Parameters
        -----------
        bot: :class:`~taho.Bot`
            The bot instance.
        server_id: Optional[:class:`int`]
            The server ID.
        
        Returns
        --------
        :class:`str`
            The display role's display string for the server.
            If the role exists in the server, it returns a mention,
            else a name.
        """
        try:
            role = await self.get_discord_role(bot, server_id)
        except DoesNotExist:
            return next(role.name for role in await self.get_discord_roles(bot))
        else:
            return role.mention

class ServerRole(BaseModel):
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
    def role_id_(self) -> int:
        """
        :class:`int`: Shortcut for :attr:`.discord_role_id`.
        """
        return self.discord_role_id

    
    async def get_guild(self, bot: Bot) -> discord.Guild:
        """|coro|

        Get the guild object corresponding to
        the role's server.

        This function is here to avoid an additional query
        to get :attr:`.ServerRole.server`.
        This function use :attr:`.ServerRole.server_id`
        to get the guild object.

        Parameters
        -----------
        bot: :class:`~taho.Bot`
            The bot instance.
        """
        return bot.get_guild(self.server_id)
        
    async def get_role(self, bot: Bot) -> discord.Role:
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
        guild = await self.get_guild(bot)
        return guild.get_role(self.discord_role_id)
