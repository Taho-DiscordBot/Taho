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
from discord.ext import commands
from babel import Locale
from taho.database import db_utils

if TYPE_CHECKING:
    from taho.database.models import (
        User,
        Cluster,
        Server
        )
    from typing import List, Optional, Union, List, Sequence
    from discord import (
        Embed, File, Message, GuildSticker, 
        StickerItem, AllowedMentions, MessageReference, 
        PartialMessage
    )
    from discord.ui import View

__all__ = (
    "TahoContext",
)

class TahoContext(commands.Context):
    
    async def babel_locale(self) -> Locale:
        if self.interaction:
            return Locale.parse(str(self.interaction.locale), sep="-")
        return Locale.parse(self.guild.preferred_locale.value, sep="-")
    
    async def get_cluster(self) -> Cluster:
        """|coro|
        
        Get the cluster where the Guild (from this context)
        is.
        
        Returns
        --------
        :class:`~taho.database.models.Cluster`
            The cluster.
        

        .. note::

            If the cluster does not exist in the DB,
            then it is created.
        """
        if hasattr(self, "cluster"):
            return self.cluster
        
        # This function will set the server attribute
        await self.get_server()
        self.cluster = await self.server.cluster

        return self.cluster
    
    async def get_cluster_id(self) -> int:
        """|coro|
        
        Get the cluster ID from the context's guild.
        """
        if hasattr(self, "cluster"):
            return self.cluster.id
        
        server = await self.get_server()

        return server.cluster_id

    async def get_server(self, *fetch_related: List[str]) -> Server:
        """|coro|

        Get the server instance corresponding to the 
        Context's :class:`discord.Guild`.

        Parameters
        -----------
        fetch_related: List[:class:`str`]
            The related fields that should be fetched
            (by Tortoise-ORM).
        
        Returns
        --------
        :class:`~taho.database.models.Server`
            The Server. 


        .. note::

            If the server does not exist in the DB,
            then it is created.
        """
        if hasattr(self, "server"):
            return self.server

        self.server = await db_utils.get_server(self.bot, self.guild, *fetch_related)

        return self.server

    async def get_user(self) -> User:
        """|coro|
        
        Get the user from the context's author.

        :func:`~taho.database.models.User.init_user` will
        be called if :attr:`~taho.database.models.User.initialized`
        is ``False``.
        """
        if hasattr(self, "user"):
            return self.user
        
        cluster_id = await self.get_cluster_id()

        self.user = await db_utils.get_user(cluster_id, self.author.id)

        return self.user

    async def init_server(self) -> None:
        """|coro|
        
        Initialize the server in the DB
        if it does not exist.
        """
        if not self.guild.id in self.bot.registered_servers:
            await self.get_server()

    async def send(
        self, 
        content: Optional[str] = None, 
        *, tts: bool = False, 
        embed: Optional[Embed] = None, 
        embeds: Optional[Sequence[Embed]] = None, 
        file: Optional[File] = None, 
        files: Optional[Sequence[File]] = None, 
        stickers: Optional[Sequence[Union[GuildSticker, StickerItem]]] = None, 
        delete_after: Optional[float] = None, 
        nonce: Optional[Union[str, int]] = None, 
        allowed_mentions: Optional[AllowedMentions] = None, 
        reference: Optional[Union[Message, MessageReference, PartialMessage]] = None, 
        mention_author: Optional[bool] = None, 
        view: Optional[View] = None, 
        suppress_embeds: bool = False, 
        ephemeral: bool = False
    ) -> Message:
        
        msg = await super().send(
            content, 
            tts=tts, 
            embed=embed, 
            embeds=embeds, 
            file=file, 
            files=files, 
            stickers=stickers, 
            delete_after=delete_after, 
            nonce=nonce, 
            allowed_mentions=allowed_mentions, 
            reference=reference, 
            mention_author=mention_author, 
            view=view, 
            suppress_embeds=suppress_embeds, 
            ephemeral=ephemeral
        )

        if view:
            view.msg = msg

        return msg

