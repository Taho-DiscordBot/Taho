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


