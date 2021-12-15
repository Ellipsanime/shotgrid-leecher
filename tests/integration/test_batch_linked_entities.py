from typing import Dict, List

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from bson import ObjectId
from mock import Mock
from mongomock.mongo_client import MongoClient

from asset import linked_entities_data
from shotgrid_leecher.controller import batch_controller
from shotgrid_leecher.record.enums import DbName
from shotgrid_leecher.utils import connectivity as conn
from utils.funcs import (
    all_intermediate,
    batch_config,
    fun,
    all_avalon,
    populate_db,
    sg_query,
)


def _intermediate_by_link_type(client: MongoClient) -> List[Dict]:
    return [x for x in all_intermediate(client) if "linked_entities" in x]


@pytest.mark.asyncio
async def test_batch_with_linked_entities_propagation_without_history(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    project_id = linked_entities_data.PROJECT_ID
    client = MongoClient()
    populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        linked_entities_data.AVALON_DATA,
    )
    sg_client = Mock()
    config = batch_config(overwrite=False)
    sg_client.find = sg_query(linked_entities_data)
    sg_client.find_one = sg_query(linked_entities_data)
    monkeypatch.setattr(conn, "get_shotgrid_client", fun(sg_client))
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await batch_controller.batch_update(project_id, config)
    # Assert
    assert_that(all_avalon(client)).extracting(
        "data", filter={"name": "SHOT10"}
    ).extracting("inputLinks").is_length(1)
    assert_that(
        [
            x["data"]["inputLinks"]
            for x in all_avalon(client)
            if x["name"] == "SHOT10"
        ][0][0]["id"]
    ).is_type_of(ObjectId)


@pytest.mark.asyncio
async def test_batch_with_linked_entities_propagation_with_history(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    project_id = linked_entities_data.PROJECT_ID
    client = MongoClient()
    populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        linked_entities_data.AVALON_DATA,
    )
    populate_db(
        client.get_database(DbName.INTERMEDIATE.value).get_collection(
            project_id
        ),
        linked_entities_data.INTERMEDIATE_DB_DATA,
    )
    sg_client = Mock()
    config = batch_config(overwrite=False)
    sg_client.find = sg_query(linked_entities_data)
    sg_client.find_one = sg_query(linked_entities_data)
    monkeypatch.setattr(conn, "get_shotgrid_client", fun(sg_client))
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await batch_controller.batch_update(project_id, config)
    # Assert
    assert_that(all_avalon(client)).extracting(
        "data", filter={"name": "SHOT10"}
    ).extracting("inputLinks").is_length(1)
    assert_that(
        [
            x["data"]["inputLinks"]
            for x in all_avalon(client)
            if x["name"] == "SHOT10"
        ][0][0]["id"]
    ).is_equal_to(
        linked_entities_data.INTERMEDIATE_DB_DATA[5]["linked_entities"][0][
            "object_id"
        ]
    )


@pytest.mark.asyncio
async def test_batch_with_linked_entities_at_intermediate_level(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    project_id = linked_entities_data.PROJECT_ID
    client = MongoClient()
    populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        linked_entities_data.AVALON_DATA,
    )
    populate_db(
        client.get_database(DbName.INTERMEDIATE.value).get_collection(
            project_id
        ),
        linked_entities_data.INTERMEDIATE_DB_DATA,
    )
    sg_client = Mock()
    config = batch_config(overwrite=False)
    sg_client.find = sg_query(linked_entities_data)
    sg_client.find_one = sg_query(linked_entities_data)
    monkeypatch.setattr(conn, "get_shotgrid_client", fun(sg_client))
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await batch_controller.batch_update(project_id, config)
    # Assert
    assert_that(_intermediate_by_link_type(client)).extracting(
        "data", filter={"name": "SHOT10"}
    )
