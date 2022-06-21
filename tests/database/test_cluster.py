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
from typing import List
import pytest
from taho.database.models import *
from .fixture import db_data

@pytest.mark.asyncio
async def test_clusters(db_data):
    clusters = db_data.clusters

@pytest.mark.asyncio
async def test_cluster_info(db_data):
    clusters: List[ServerCluster] = db_data.clusters
    await clusters[0].set_info("test1", "test")
    await clusters[0].set_info("test2", None)
    await clusters[0].set_info("test3", True)
    await clusters[0].set_info("test4", 3)
    await clusters[0].set_info("test5", 3.14)
    assert await clusters[0].get_info("test1") == "test"
    assert await clusters[0].get_info("test2") is None
    assert await clusters[0].get_info("test3") is True
    assert await clusters[0].get_info("test4") == 3
    assert await clusters[0].get_info("test5") == 3.14
    with pytest.raises(KeyError):
        await clusters[0].get_info("test6")
    
    await clusters[1].set_info("test1", "test2")
    assert await clusters[1].get_info("test1") == "test2"


