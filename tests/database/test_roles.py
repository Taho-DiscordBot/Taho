import pytest
from taho.database.models import *
from .test_initialize_db import clusters, guilds, users, npcs

@pytest.fixture
async def roles(clusters):
    _roles = pytest.test_data["discord"]["roles"]
    _guilds = pytest.test_data["discord"]["guilds"]
    return [
        await clusters[0].create_role(pytest.bot, _roles[_guilds[0]][0], RoleType.DEFAULT),
        await clusters[1].create_role(pytest.bot, _roles[_guilds[2]][0], RoleType.DEFAULT),
    ]

@pytest.mark.asyncio
async def test_roles(roles, clusters):
    assert len(roles) == 2
    assert roles[0].cluster == clusters[0]
    assert roles[1].cluster == clusters[1]
    assert roles[0].type == RoleType.DEFAULT
    assert roles[1].type == RoleType.DEFAULT
    assert len(await roles[0].guild_roles.all()) == 2
    assert len(await roles[1].guild_roles.all()) == 1