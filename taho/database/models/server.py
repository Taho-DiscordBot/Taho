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
from .base import BaseModel
from tortoise import fields
from tortoise import exceptions as t_exceptions
from ..utils import convert_to_type, get_type
from taho.enums import InfoType

if TYPE_CHECKING:
    from typing import Optional, Union
    import discord
    from taho import Bot


__all__ = (
    "Server",
    "ServerInfo",
)

class Server(BaseModel):
    """
    Represents a Server.

    .. container:: operations

        .. describe:: x == y

            Checks if two servers are equal.

        .. describe:: x != y

            Checks if two servers are not equal.
        
        .. describe:: hash(x)

            Returns the server's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: cluster

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Cluster`
                - :attr:`related_name` ``servers``
            
            Python: :class:`~taho.database.models.Cluster`       
    
    Attributes
    -----------
    id: :class:`int`
        The server's ID.
    cluster: :class:`~taho.database.models.Cluster`
        The cluster the server is in.
    infos: List[:class:`.ServerInfo`]
        |coro_attr|

        The server's info.
    

    .. note::

        When you create a server, please set the ID as that of 
        the attached :class:`discord.Guild`.

        Example:

            My guild (ID: 123456789) ::

                server = Server.create(id=123456789)

    """
    class Meta:
        table = "servers"

    id = fields.BigIntField(pk=True)
    cluster = fields.ForeignKeyField("main.Cluster", related_name="servers")

    infos: fields.ReverseRelation["ServerInfo"]

    async def get_info(self, key: str) -> Optional[Union[str, int, float, None]]:
        """|coro|

        Returns the value of a key in the server's info.

        Parameters
        -----------
        key: :class:`str`
            The key of the info.
        
        Raises
        -------
        KeyError
            If the key does not exist.
        
        Returns
        --------
        Union[``None``, :class:`bool`, :class:`int`, :class:`float`, :class:`str`]
            The value of the key. 


        .. note::

            If the key is not found in server's info,
            then the function search in cluster's ones.       
        """
        try:
            info = await ServerInfo.get(server=self, key=key)
            return info.py_value
        except t_exceptions.DoesNotExist:
            return await (await self.cluster).get_info(key)
    
    async def set_info(self, key: str, value: Optional[Union[str, int, float, None]]) -> None:
        """|coro|

        Sets the value of a key in the server's info.

        Parameters
        -----------
        key: :class:`str`
            The key of the info.
        value: Union[``None``, :class:`bool`, :class:`int`, :class:`float`, :class:`str`]
            The value of the key.
        """
        # If the info already exists, update it.
        await ServerInfo.update_or_create(
            server=self, 
            key=key,
            type=get_type(value),
            value=str(value)
        )

    async def get_guild(self, bot: Bot) -> Optional[discord.Guild]:
        """|coro|

        Get the :class:`discord.Guild` object of the server.

        Parameters
        -----------
        bot: :class:`~taho.Bot`
            The bot instance.
        
        Returns
        --------
        Optional[class:`discord.Guild`]
            The guild object, if found.
        """
        guild = bot.get_guild(self.id)
        if guild and not guild.chunked:
            await guild.chunk()
        return guild
    
    async def get_member(self, bot: Bot, user_id: int) -> Optional[discord.Member]:
        """|coro|

        Get a :class:`discord.Member` from the server's guild.

        Parameters
        -----------
        bot: :class:`~taho.Bot`
            The bot instance.
        user_id: :class:`int`
            The user's ID.
        
        Returns
        --------
        Optional[:class:`discord.Member`]
            The member object, if found.
        """
        return (await self.get_guild(bot)).get_member(user_id)
    
    async def get_role(self, bot: Bot, role_id: int) -> Optional[discord.Role]:
        """|coro|

        Get a :class:`discord.Role` from the server's guild.

        Parameters
        -----------
        bot: :class:`~taho.Bot`
            The bot instance.
        role_id: :class:`int`
            The role's ID.
        
        Returns
        --------
        Optional[:class:`discord.Role`]
            The role object, if found.
        """
        return (await self.get_guild(bot)).get_role(role_id)

class ServerInfo(BaseModel):
    """
    Represents a server's info.

    .. container:: operations

        .. describe:: x == y

            Checks if two info are equal.
            The two :attr:`.py_value` are compared.
        
        .. describe:: x != y

            Checks if two info are different.
            The two :attr:`.py_value` are compared.
        
        .. describe:: hash(x)

            Returns the info's hash.
        
        .. describe:: str(x)

            Returns the info as a string.
    
    .. container:: fields

        .. collapse:: id

            Tortoise: :class:`tortoise.fields.IntField`

                - :attr:`pk` True
            
            Python: :class:`int`
        
        .. collapse:: server

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`.Server`
                - :attr:`related_name` ``infos``
            
            Python: :class:`.Server`
        
        .. collapse:: key

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
            
            Python: :class:`str`
        
        .. collapse:: type

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.InfoType`
            
            Python: :class:`~taho.enums.InfoType`
        
        .. collapse:: value

            Tortoise: :class:`tortoise.fields.CharField`

                - :attr:`max_length` ``255``
            
            Python: :class:`str`
        
    Attributes
    -----------
    server: :class:`.Server`
        The server the info belongs to.
    key: :class:`str`
        The key of the info.
    type: :class:`~taho.enums.InfoType`
        The type of the info.
    value: :class:`str`
        The value of the info.
    py_value: Union[``None``, :class:`bool`, :class:`int`, :class:`float`, :class:`str`]
        The value of the info in Python's type.
    """
    class Meta:
        table = "server_infos"

    id = fields.IntField(pk=True)

    server = fields.ForeignKeyField("main.Server", related_name="infos")
    key = fields.CharField(max_length=255)
    type = fields.IntEnumField(InfoType)
    value = fields.CharField(max_length=255)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ServerInfo):
            return self.py_value == other.py_value
        return other == self.py_value
    
    def __str__(self) -> str:
        return self.value
    
    @property
    def py_value(self) -> Union[None, bool, int, float, str]:
        return convert_to_type(self.value, self.type)