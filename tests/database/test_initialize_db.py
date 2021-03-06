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
import pytest
from taho.database.models import *
from .fixture import db_data


@pytest.mark.asyncio
async def test_init_clusters(db_data):
    clusters = db_data.clusters
    assert len(clusters) == 2
    assert clusters[0].name == "Cluster A"
    assert clusters[1].name == "Cluster B"


@pytest.mark.asyncio
async def test_init_guilds(db_data):
    clusters = db_data.clusters
    guilds = db_data.guilds
    assert len(guilds) == 3
    assert guilds[0].cluster == clusters[0]
    assert guilds[1].cluster == clusters[0]
    assert guilds[2].cluster == clusters[1]


@pytest.mark.asyncio
async def test_init_users(db_data):
    clusters = db_data.clusters
    users = db_data.users
    _users = pytest.test_data["discord"]["users"]
    assert len(users) == 4
    assert users[0].cluster == clusters[0]
    assert users[1].cluster == clusters[0]
    assert users[2].cluster == clusters[1]
    assert users[3].cluster == clusters[1]
    assert users[0].user_id == _users[0].id
    assert users[1].user_id == _users[1].id
    assert users[2].user_id == _users[0].id
    assert users[3].user_id == _users[1].id

@pytest.mark.asyncio
async def test_init_npcs(db_data):
    clusters = db_data.clusters
    npcs = db_data.npcs
    assert len(npcs) == 4
    assert npcs[0].cluster == clusters[0]
    assert npcs[1].cluster == clusters[0]
    assert npcs[2].cluster == clusters[1]
    assert npcs[3].cluster == clusters[1]
    assert npcs[0].name == "NPC 1"
    assert npcs[1].name == "NPC 2"
    assert npcs[2].name == "NPC 3"
    assert npcs[3].name == "NPC 4"

@pytest.mark.asyncio
async def test_init_npc_owners(db_data):
    users = db_data.users
    npcs = db_data.npcs
    npc_owners = db_data.npc_owners
    assert len(npc_owners) == 6
    assert npc_owners[0].npc == npcs[0]
    assert npc_owners[0].user == users[0]
    assert npc_owners[0].original_owner
    assert npc_owners[1].npc == npcs[0]
    assert npc_owners[1].user == users[1]
    assert not npc_owners[1].original_owner
    assert npc_owners[2].npc == npcs[1]
    assert npc_owners[2].user == users[0]
    assert npc_owners[2].original_owner
    assert npc_owners[3].npc == npcs[2]
    assert npc_owners[3].user == users[2]
    assert npc_owners[3].original_owner
    assert npc_owners[4].npc == npcs[2]
    assert npc_owners[4].user == users[3]
    assert not npc_owners[4].original_owner
    assert npc_owners[5].npc == npcs[3]
    assert npc_owners[5].user == users[2]
    assert npc_owners[5].original_owner




