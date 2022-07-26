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
from tortoise import exceptions as t_exceptions
from taho.exceptions import DoesNotExist, AlreadyExists

if TYPE_CHECKING:
    from ..models import Server, Cluster, Currency, User
    from taho import Bot
    from typing import List, Optional
    import discord

__all__ = (
    "get_server",
    "new_server",
    "get_cluster",
    "get_default_currency",
    "get_default_user",
    "get_user",
)

async def get_server(bot: Bot, guild: discord.Guild, *fetch_related: List[str]) -> Server:
    """|coro|

    Get the server instance corresponding to the 
    :class:`discord.Guild`.

    Parameters
    -----------
    guild: :class:`discord.Guild`
        The guild to get the server instance for.
    fetch_related: List[:class:`str`]
        The related fields that should be fetched
        (by Tortoise-ORM).
    
    Returns
    --------
    :class:`~taho.database.models.Server`
        The Server. 


    .. note::

        If the server does not exist in the DB,
        then it is created using :func:`~taho.database.utils.new_server`. 
    """
    from taho.database.models import Server
    try:
        server = await Server.from_guild(guild)
        if fetch_related:
            await server.fetch_related(*fetch_related)
        return server
    except DoesNotExist:
        return await new_server(bot, guild, *fetch_related)

async def new_server(bot: Bot, guild: discord.Guild, *fetch_related: List[str]) -> Server:
    """|coro|
    
    Initialize a server in the DB.

    Parameters
    -----------
    bot: :class:`~taho.Bot`
        The bot instance.
    guild: :class:`discord.Guild`
        The guild to initialize the server for.
    fetch_related: List[:class:`str`]
        The related fields that should be fetched
        from the server (by Tortoise-ORM).
    
    Raises
    -------
    :class:`taho.exceptions.AlreadyExists`
        If the server is already initialized.
    
    Returns
    --------
    :class:`~taho.database.models.Server`
        The Server.
    """
    from taho.database.models import Server, Cluster # avoid circular import
    try:
        await Server.from_guild(guild)
    except DoesNotExist:
        pass
    else:
        raise AlreadyExists("Server already initialized.")

    cluster = await Cluster.create()

    server = await cluster.add_guild(bot, guild, sync_server=False)

    if fetch_related:
        await server.fetch_related(*fetch_related)

    return server

async def get_cluster(guild: discord.Guild) -> Cluster:
    pass

async def get_default_currency(cluster_id: int) -> Optional[Currency]:
    """|coro|

    Get the default Currency of the cluster.
    
    Returns
    --------
    Optional[:class:`~taho.database.models.Currency`]
        The default currency of the cluster.
    """
    from taho.database.models import Currency # avoid circular import

    try:
        return await Currency.get(cluster_id=cluster_id, is_default=True)
    except t_exceptions.DoesNotExist:
        return None

async def get_default_user(cluster_id: int) -> User:
    """|coro|

    Get the default User of the cluster.

    If the cluster has no default user, then it 
    is created.
    
    Returns
    --------
    :class:`~taho.database.models.User`
        The default user of the cluster.
    """
    from taho.database.models import User # avoid circular import
    
    user = await User.get_or_create(cluster_id=cluster_id, user_id=0)
    return user[0]

async def get_user(cluster_id: int, user_id: int) -> User:
    """|coro|

    Get a user of a cluster.

    If the user does not exist, then it is created.
    
    Returns
    --------
    :class:`~taho.database.models.User`
        The user of the cluster.
    """
    from taho.database.models import User # avoid circular import
    
    user = await User.get_or_create(cluster_id=cluster_id, user_id=user_id)
    return user[0]