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
            (await ServerCluster.get_or_create(name="Cluster A"))[0],
            (await ServerCluster.get_or_create(name="Cluster B"))[0],
        ]

        _guilds = pytest.test_data["discord"]["guilds"]
        self.guilds =  [
            (await Guild.get_or_create(cluster=self.clusters[0], id=_guilds[0].id))[0],
            (await Guild.get_or_create(cluster=self.clusters[0], id=_guilds[1].id))[0],
            (await Guild.get_or_create(cluster=self.clusters[1], id=_guilds[2].id))[0],
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

