from itertools import chain
from typing import Dict, List

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from mock import Mock
from mongomock.mongo_client import MongoClient

from asset import linked_entities_data
from shotgrid_leecher.controller import batch_controller
from shotgrid_leecher.record.enums import DbName
from shotgrid_leecher.repository import config_repo
from shotgrid_leecher.utils import connectivity as conn
from shotgrid_leecher.utils.ids import to_object_id
from utils.funcs import (
    all_intermediate,
    batch_config,
    fun,
    all_avalon,
    populate_db,
    sg_query, creds,
)


def _intermediate_entity_links(client: MongoClient) -> List[Dict]:
    return list(
        chain(
            *[
                x["linked_entities"]
                for x in all_intermediate(client)
                if "linked_entities" in x
            ]
        )
    )


def _avalon_input_links(client: MongoClient) -> List[Dict]:
    return list(
        chain(
            *[
                [
                    {**y, "name": x["name"]}
                    for y in x.get("data", dict()).get("inputLinks", [])
                ]
                for x in all_avalon(client)
                if x.get("data", dict()).get("inputLinks")
            ]
        )
    )


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
    monkeypatch.setattr(config_repo, "find_credentials_by_url", creds)
    # Act
    await batch_controller.batch_update(project_id, config)
    # Assert
    assert_that(_avalon_input_links(client)).is_length(6)
    assert_that(_avalon_input_links(client)).extracting(
        "id", filter={"name": "Fork1"}
    ).is_equal_to([to_object_id(11001000), to_object_id(-11001000)])
    assert_that(_avalon_input_links(client)).extracting(
        "quantity", filter={"name": "Fork1"}
    ).is_equal_to([15, 1])
    assert_that(_avalon_input_links(client)).extracting(
        "id", filter={"name": "SHOT10"}
    ).is_equal_to(
        [
            to_object_id(88_888),
            to_object_id(-88_888),
            to_object_id(99_999),
            to_object_id(-99_999),
        ]
    )
    assert_that(_avalon_input_links(client)).extracting(
        "quantity", filter={"name": "SHOT10"}
    ).is_equal_to([5, 1, 2, 1])


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
    monkeypatch.setattr(config_repo, "find_credentials_by_url", creds)
    # Act
    await batch_controller.batch_update(project_id, config)
    # Assert
    assert_that(_intermediate_entity_links(client)).extracting(
        "link_type", filter={"link_type": "AssetAssetConnection"}
    ).is_length(2)
    assert_that(_intermediate_entity_links(client)).extracting(
        "object_id", filter={"link_type": "AssetAssetConnection"}
    ).is_equal_to([to_object_id(11001000), to_object_id(-11001000)])
    assert_that(_intermediate_entity_links(client)).extracting(
        "quantity", filter={"link_type": "AssetAssetConnection"}
    ).is_equal_to([15, 1])
    assert_that(_intermediate_entity_links(client)).extracting(
        "link_type", filter={"link_type": "AssetShotConnection"}
    ).is_length(2)
    assert_that(_intermediate_entity_links(client)).extracting(
        "object_id", filter={"link_type": "AssetShotConnection"}
    ).is_equal_to([to_object_id(88_888), to_object_id(-88_888)])
    assert_that(_intermediate_entity_links(client)).extracting(
        "quantity", filter={"link_type": "AssetShotConnection"}
    ).is_equal_to([5, 1])
    assert_that(_intermediate_entity_links(client)).extracting(
        "link_type", filter={"link_type": "ShotShotConnection"}
    ).is_length(2)
    assert_that(_intermediate_entity_links(client)).extracting(
        "object_id", filter={"link_type": "ShotShotConnection"}
    ).is_equal_to([to_object_id(99_999), to_object_id(-99_999)])
    assert_that(_intermediate_entity_links(client)).extracting(
        "quantity", filter={"link_type": "ShotShotConnection"}
    ).is_equal_to([2, 1])
