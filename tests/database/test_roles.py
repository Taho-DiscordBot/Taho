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
from .test_initialize_db import clusters, guilds, users, npcs

@pytest.fixture
async def roles(clusters):
    _roles = pytest.test_data["discord"]["roles"]
    _guilds = pytest.test_data["discord"]["guilds"]
    return [
        await clusters[0].create_role(pytest.bot, _roles[_guilds[0]][0], RoleType.default),
        await clusters[1].create_role(pytest.bot, _roles[_guilds[2]][0], RoleType.default),
    ]

@pytest.mark.asyncio
async def test_roles(roles, clusters):
    assert len(roles) == 2
    assert roles[0].cluster == clusters[0]
    assert roles[1].cluster == clusters[1]
    assert roles[0].type == RoleType.default
    assert roles[1].type == RoleType.default
    assert len(await roles[0].guild_roles.all()) == 2
    assert len(await roles[1].guild_roles.all()) == 1