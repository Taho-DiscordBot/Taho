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
from typing import TYPE_CHECKING, Union
import discord
from taho.database.models import *
from taho.exceptions import DoesNotExist, TahoException
from taho.enums import *
from taho import Emoji


if TYPE_CHECKING:
    from taho.bot import Bot
    from typing import List, Union, Dict

__all__ = (
    "check_guilds_test",
    "setup_db_test",
)

class NoTestGuilds(TahoException):
    """
    Raised when you run :function:`.setup_db_test`
    and there is not 3 test guilds created.
    """
    pass

class UsersNotInGuilds(TahoException):
    """
    Raised when you run :function:`.setup_db_test`
    and there is not at least two users in the guilds.
    """
    pass

async def check_guilds_test(bot: Bot) -> Dict[str, Union[List[discord.Guild], List[int]]]:
    """|coro|

    Check if the 3 tests guilds are created and valid.

    .. note::

        To run tests, you have to create 3 guilds:
        - Taho Unit Test 1
        - Taho Unit Test 2
        - Taho Unit Test 3
        with this template: https://discord.new/GKkm4xd2yGv9.

        You also have to join these 3 guilds with at least 2 differents
        Discord accounts, and the bot must be in.
    
    Parameters
    -----------
    bot: :class:`~taho.Bot`
        The bot instance.
    
    Raises
    --------
    .NoTestGuilds
        If there is not 3 test guilds created.
    .UsersNotInGuilds
        If there is not at least two users in the guilds.
    
    Returns
    --------
    Dict[str, Union[List[:class:`discord.Guild`], List[:class:`int`]]]
        A dict with the 3 test guilds and the two user's ids.
        Format: ::

            {
                'guilds': List[discord.guild];
                'users': List[int]
            }
    """
    guilds = []
    users = []
    for i in range(1, 4):
        guild = discord.utils.find(lambda g: g.name == f"Taho Unit Test {i}", bot.guilds)
        if not guild:
            raise NoTestGuilds(f"The guild Taho Unit Test {i} is not created or the bot is not in.")
        await guild.chunk()
        if guild.member_count < 3:
            raise UsersNotInGuilds(f"The guild Taho Unit Test {i} has not at least 2 users.")
        for m in guild.members:
            if m.id not in users and m.id != bot.user.id:
                users.append(m.id)
        guilds.append(guild)
    return {
        "guilds": guilds,
        "users": users
    }

async def setup_db_test(bot: Bot) -> List[str]:
    """|coro|
    
    Setup the database for testing purposes.
    The function will create data for every systems
    of the bot, to help you perform tests.

    .. warning:: 

        - This function will delete some data from the database.
        - Use it only for testing purposes (in developpement 
        environments).
        - To run this command, you have to first call 
        :function:`.setup_guilds_test` to create the guilds
        and joind these guilds whese at least two differents 
        Discord accounts.

    Parameters
    -----------
    bot: :class:`~taho.Bot`
        The bot instance.
    
    Raises
    --------
    .NoTestGuilds
        If there is not 3 test guilds created.
    .UsersNotInGuilds
        If there is not at least two users in the guilds.

    Returns
    --------
    List[:class:`str`]
        A list of invitations to the 3 guilds created.
    
    .. note:: 

        The 3 guilds are created with the name ``Taho Unit Test 1``,
        2 & 3, please don't change the name of the guilds.
    """
    data = await check_guilds_test(bot)
    guilds = data["guilds"]
    members = data["users"]
    
    # Clear data
    for guild in guilds:
        try:
            cluster = await Cluster.from_guild(bot, guild)
            await cluster.delete()
        except DoesNotExist:
            continue
    
    # Create new data
    clusters = [
        await Cluster.create(name="Cluster A"),
        await Cluster.create(name="Cluster B"),
    ]
    servers = [
        await Server.create(cluster=clusters[0], id=guilds[0].id),
        await Server.create(cluster=clusters[0], id=guilds[1].id),
        await Server.create(cluster=clusters[1], id=guilds[2].id),
    ]
    users = [
        await User.create(cluster=clusters[0], user_id=members[0]),
        await User.create(cluster=clusters[0], user_id=members[1]),
        await User.create(cluster=clusters[1], user_id=members[0]),
        await User.create(cluster=clusters[1], user_id=members[1]),
    ]
    npcs = [
        await NPC.create(cluster=clusters[0], name="NPC 1"),
        await NPC.create(cluster=clusters[0], name="NPC 2"),
        await NPC.create(cluster=clusters[1], name="NPC 3"),
        await NPC.create(cluster=clusters[1], name="NPC 4"),
    ]
    npc_owners = [
        await NPCOwner.create(npc=npcs[0], user=users[0], original_owner=True),
        await NPCOwner.create(npc=npcs[0], user=users[1]),
        await NPCOwner.create(npc=npcs[1], user=users[0], original_owner=True),
        await NPCOwner.create(npc=npcs[2], user=users[2], original_owner=True),
        await NPCOwner.create(npc=npcs[2], user=users[3]),
        await NPCOwner.create(npc=npcs[3], user=users[2], original_owner=True),
    ]
    items_data = [
        {
            "name": "Item 1",
            "emoji": Emoji(bot, "💎"),
            "description": "This is an item",
            "type": ItemType.resource,
        },
        {
            "name": "Item 2",
            "type": ItemType.consumable,
            "durability": 5,
            "cooldown": 5
        },
        {
            "name": "Item 3",
            "type": ItemType.consumable,
            "durability": 5,
        }
    ]
    items = []
    for cluster in clusters:
        for item_data in items_data:
            item = await cluster.create_item(**item_data)
            items.append(item)
            
    items[0].edit(name="Item 1 edited")
    items[2].ammo_id = items[0].id
    items[2].charger_size = -1
    await items[2].save()
    items[5].ammo_id = items[3].id
    items[5].charger_size = 5
    await items[5].save()
    



    return None
