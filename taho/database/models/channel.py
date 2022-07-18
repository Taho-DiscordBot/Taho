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
from taho.enums import ChannelType

__all__ = (
    "ServerChannel",
)

class ServerChannel(BaseModel):
    """
    Represents a channel of a Server.

    .. container:: operations

        .. describe:: x == y

            Checks if two channels are equal.

        .. describe:: x != y

            Checks if two channels are not equal.
        
        .. describe:: hash(x)

            Returns the channel's hash.
        
    .. container:: fields

        .. collapse:: id
            
            Tortoise: :class:`tortoise.fields.BigIntField`

                - :attr:`pk` True

            Python: :class:`int`
        
        .. collapse:: server

            Tortoise: :class:`tortoise.fields.ForeignKeyField`

                - :attr:`related_model` :class:`~taho.database.models.Server`
                - :attr:`related_name` ``rp_channels``

            Python: :class:`~taho.database.models.Server`
        
        .. collapse:: webhook_url

            Tortoise: :class:`tortoise.fields.TextField`

                - :attr:`null` ``True``

            Python: Optional[:class:`str`]
        
        .. collapse:: type

            Tortoise: :class:`tortoise.fields.IntEnumField`

                - :attr:`enum` :class:`~taho.enums.ChannelType`
                - :attr:`default` :attr:`~taho.enums.ChannelType.other`
            
            Python: :class:`~taho.enums.ChannelType`

    Attributes
    -----------
    id: :class:`int`
        The channel's ID.
    server: :class:`~taho.database.models.Server`
        The server the channel belongs to.
    webhook_url: Optional[:class:`str`]
        The channel's webhook URL.
    type: :class:`~taho.enums.ChannelType`
        The channel's type.
    

    .. note::

        When you create a channel, please set the ID as that of 
        the attached :class:`discord.TextChannel`.

        Example:

            My channel (ID: 123456789) ::

                Server = ServerChannel.create(id=123456789, ...)
    

    .. note:: 

        When a channel is created, the same :attr:`.ServerChannel.type` is 
        associated with all its threads
    """

    class Meta:
        table = "server_channels"
    
    id = fields.BigIntField(pk=True)
    server = fields.ForeignKeyField("main.Server", related_name="rp_channels")
    webhook_url = fields.TextField(null=True)
    type = fields.IntEnumField(ChannelType, default=ChannelType.other)
