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


class TestData:
    def __init__(self) -> None:
        self.clusters = []
        self.guilds = []
        self.users = []
        self.npcs = []
        self.npc_owners = []

    async def load(self) -> None:
        self.clusters = [
            (await Cluster.get_or_create(name="Cluster A"))[0],
            (await Cluster.get_or_create(name="Cluster B"))[0],
        ]

        _guilds = pytest.test_data["discord"]["guilds"]
        self.guilds =  [
            (await Server.get_or_create(cluster=self.clusters[0], id=_guilds[0].id))[0],
            (await Server.get_or_create(cluster=self.clusters[0], id=_guilds[1].id))[0],
            (await Server.get_or_create(cluster=self.clusters[1], id=_guilds[2].id))[0],
        ]

        _users = pytest.test_data["discord"]["users"]
        self.users = [
            (await User.get_or_create(cluster=self.clusters[0], user_id=_users[0].id))[0],
            (await User.get_or_create(cluster=self.clusters[0], user_id=_users[1].id))[0],
            (await User.get_or_create(cluster=self.clusters[1], user_id=_users[0].id))[0],
            (await User.get_or_create(cluster=self.clusters[1], user_id=_users[1].id))[0],
        ]

        self.npcs = [
            (await NPC.get_or_create(cluster=self.clusters[0], name="NPC 1"))[0],
            (await NPC.get_or_create(cluster=self.clusters[0], name="NPC 2"))[0],
            (await NPC.get_or_create(cluster=self.clusters[1], name="NPC 3"))[0],
            (await NPC.get_or_create(cluster=self.clusters[1], name="NPC 4"))[0],
        ]

        self.npc_owners = [
            (await NPCOwner.get_or_create(npc=self.npcs[0], user=self.users[0], original_owner=True))[0],
            (await NPCOwner.get_or_create(npc=self.npcs[0], user=self.users[1]))[0],
            (await NPCOwner.get_or_create(npc=self.npcs[1], user=self.users[0], original_owner=True))[0],
            (await NPCOwner.get_or_create(npc=self.npcs[2], user=self.users[2], original_owner=True))[0],
            (await NPCOwner.get_or_create(npc=self.npcs[2], user=self.users[3]))[0],
            (await NPCOwner.get_or_create(npc=self.npcs[3], user=self.users[2], original_owner=True))[0],
        ]


@pytest.fixture()
async def db_data():
    if not "db_data" in pytest.test_data:
        pytest.test_data["db_data"] = TestData()
        await pytest.test_data["db_data"].load()
    return pytest.test_data["db_data"]

