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
import asyncio
import pytest
import discord
from discord.ext.commands import Bot
from . import config as _config
from taho.utils.ssh_tunnel_forwarder import init_ssh_tunnel
from taho.database import init_db
from taho.database.models import *
from tortoise import Tortoise

def pytest_configure():
    intents = discord.Intents.default()
    intents.message_content = True
    pytest.intents = intents
    pytest.bot = None
    pytest.test_data = {
        "discord": {},
        "db": {},
    }
    pytest.ssh_tunnel = None

@pytest.fixture(autouse=True)
async def bot(event_loop):
    pytest.bot = Bot("!", intents=pytest.intents, loop=event_loop)
    await pytest.bot.login(token=_config.TOKEN)
    return pytest.bot

@pytest.fixture(autouse=True)
async def connect_db(request):
    config = vars(_config)
    pytest.bot.config = config
    if config.get("USE_SSH_TUNNEL", False):
        ssh_tunnel = init_ssh_tunnel(config)
        ssh_tunnel.start()
    else:
        ssh_tunnel = None
    pytest.ssh_tunnel = ssh_tunnel

    await init_db(pytest.bot, ssh_tunnel)

    conn = Tortoise.get_connection('default')
    await conn.execute_script("""
    DROP TABLE IF EXISTS guild_clusters CASCADE;
    DROP TABLE IF EXISTS guilds CASCADE;
    DROP TABLE IF EXISTS users CASCADE;
    DROP TABLE IF EXISTS banks CASCADE;
    DROP TABLE IF EXISTS guild_infos CASCADE;
    DROP TABLE IF EXISTS cluster_infos CASCADE;
    DROP TABLE IF EXISTS bank_accounts CASCADE;
    DROP TABLE IF EXISTS bank_operations CASCADE;
    DROP TABLE IF EXISTS bank_infos CASCADE;
    DROP TABLE IF EXISTS items CASCADE;
    DROP TABLE IF EXISTS inventories CASCADE;
    DROP TABLE IF EXISTS roles CASCADE;
    DROP TABLE IF EXISTS stats CASCADE;
    DROP TABLE IF EXISTS item_roles CASCADE;
    DROP TABLE IF EXISTS item_stats CASCADE;
    DROP TABLE IF EXISTS jobs CASCADE;
    DROP TABLE IF EXISTS job_rewards CASCADE;
    DROP TABLE IF EXISTS npcs CASCADE;
    DROP TABLE IF EXISTS npc_roles CASCADE;
    DROP TABLE IF EXISTS npc_owners CASCADE;
    """)

    await Tortoise.generate_schemas()

    request.addfinalizer(close_db)

@pytest.fixture(autouse=True)
async def initialize_bot(bot):
    guilds = [
        await bot.fetch_guild(guild_id)
        for guild_id in _config.TEST_GUILDS
    ]
    members = {}
    for guild in guilds:
        for member_id in _config.TEST_USERS:
            if not guild in members:
                members[guild] = []
            member = await guild.fetch_member(member_id)
            if member:
                members[guild].append(member)
    
    roles = {
        guild: [r for r in guild.roles if r.name != pytest.bot.user.name]
        for guild in guilds
    }
    pytest.test_data["discord"]["guilds"] = guilds
    pytest.test_data["discord"]["members"] = members
    pytest.test_data["discord"]["users"] = list(members.values())[0]
    pytest.test_data["discord"]["roles"] = roles

@pytest.fixture(autouse=True)
async def initialize_db(request):
    return
    bot = pytest.bot

    clusters = await ServerCluster.bulk_create([
        ServerCluster(name="Cluster A"),
        ServerCluster(name="Cluster B"),
    ],
    batch_size=2
    )

    _guilds = pytest.test_data["discord"]["guilds"]
    guilds = await Guild.bulk_create([
        Guild(cluster=clusters[0], id=_guilds[0].id),
        Guild(cluster=clusters[0], id=_guilds[1].id),
        Guild(cluster=clusters[1], id=_guilds[2].id),
    ],
    batch_size=2
    )

    _users = pytest.test_data["discord"]["members"][_guilds[0]]
    users = await User.bulk_create([
        User(cluster=clusters[0], user_id=_users[0].id),
        User(cluster=clusters[0], user_id=_users[1].id),
        User(cluster=clusters[1], user_id=_users[0].id),
        User(cluster=clusters[1], user_id=_users[1].id),
    ],
    batch_size=4
    )

    npcs = await NPC.bulk_create([
        NPC(cluster=clusters[0], name="NPC 1"),
        NPC(cluster=clusters[0], name="NPC 2"),
        NPC(cluster=clusters[1], name="NPC 4"),
        NPC(cluster=clusters[1], name="NPC 4"),
    ],
    batch_size=4
    )

    npc_owners = await NPCOwner.bulk_create([
        NPCOwner(npc=npcs[0], user=users[0], original_owner=True),
        NPCOwner(npc=npcs[0], user=users[1]),
        NPCOwner(npc=npcs[1], user=users[0], original_owner=True),
        NPCOwner(npc=npcs[2], user=users[2], original_owner=True),
        NPCOwner(npc=npcs[2], user=users[3]),
        NPCOwner(npc=npcs[3], user=users[2], original_owner=True),
    ],
    batch_size=6
    )

    _roles = pytest.test_data["discord"]["roles"]
    roles = [
        await clusters[0].create_role(bot, _roles[_guilds[0]], RoleType.DEFAULT),
        await clusters[1].create_role(bot, _roles[_guilds[2]], RoleType.DEFAULT),
    ]

    npc_roles = await NPCRole.bulk_create([

    ],
    batch_size=8
    )

    jobs = await Job.bulk_create([
        Job(cluster=clusters[0], name="test1"),
        Job(cluster=clusters[0], name="test2"),
        Job(cluster=clusters[1], name="test3"),
        Job(cluster=clusters[1], name="test4"),
    ],
    batch_size=4
    )



    pytest.test_data["db"]["clusters"] = clusters
    pytest.test_data["db"]["guilds"] = guilds



def close_db():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Tortoise.close_connections())
    if pytest.ssh_tunnel:
        pytest.ssh_tunnel.stop()
