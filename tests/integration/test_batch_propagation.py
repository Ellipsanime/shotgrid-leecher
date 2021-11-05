import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from mock import Mock
from mongomock.mongo_client import MongoClient

from asset import propagation_data
from shotgrid_leecher.controller import batch_controller
from shotgrid_leecher.record.enums import DbName, AvalonType
from shotgrid_leecher.utils import connectivity as conn
from utils.funcs import (
    batch_config,
    fun,
    all_avalon,
    populate_db,
    sg_query,
)


@pytest.mark.asyncio
async def test_batch_propagation_without_project_recreation(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    project_id = propagation_data.PROJECT_ID
    client = MongoClient()
    populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        propagation_data.AVALON_DATA,
    )
    sg_client = Mock()
    config = batch_config(overwrite=False)
    sg_client.find = sg_query(propagation_data)
    sg_client.find_one = sg_query(propagation_data)
    monkeypatch.setattr(conn, "get_shotgrid_client", fun(sg_client))
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await batch_controller.batch_update(project_id, config)
    # Assert
    assert_that(all_avalon(client)).extracting(
        "name", filter={"type": "project"}
    ).is_length(1)
    assert_that(all_avalon(client)).extracting(
        "data", filter={"type": "project"}
    ).is_equal_to([propagation_data.AVALON_DATA[0]["data"]])


@pytest.mark.asyncio
async def test_batch_with_project_to_children_fps_propagation(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    project_id = propagation_data.PROJECT_ID
    client = MongoClient()
    populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        propagation_data.AVALON_DATA,
    )
    sg_client = Mock()
    config = batch_config(overwrite=False)
    sg_client.find = sg_query(propagation_data)
    sg_client.find_one = sg_query(propagation_data)
    monkeypatch.setattr(conn, "get_shotgrid_client", fun(sg_client))
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await batch_controller.batch_update(project_id, config)
    # Assert
    assert_that(all_avalon(client)).extracting(
        "data", filter={"type": "asset"}
    ).extracting("fps").is_equal_to(
        [
            propagation_data.AVALON_DATA[0]["data"].get("fps")
            for _ in [
                x
                for x in all_avalon(client)
                if x["type"] == AvalonType.ASSET.value
            ]
        ]
    )


@pytest.mark.asyncio
async def test_batch_with_project_to_children_tools_env_propagation(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    project_id = propagation_data.PROJECT_ID
    client = MongoClient()
    populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        propagation_data.AVALON_DATA,
    )
    sg_client = Mock()
    config = batch_config(overwrite=False)
    sg_client.find = sg_query(propagation_data)
    sg_client.find_one = sg_query(propagation_data)
    monkeypatch.setattr(conn, "get_shotgrid_client", fun(sg_client))
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await batch_controller.batch_update(project_id, config)
    # Assert
    assert_that(all_avalon(client)).extracting(
        "data", filter={"type": "asset"}
    ).extracting("tools_env").is_equal_to(
        [
            propagation_data.AVALON_DATA[0]["data"].get("tools_env")
            for _ in [
                x
                for x in all_avalon(client)
                if x["type"] == AvalonType.ASSET.value
            ]
        ]
    )


@pytest.mark.asyncio
async def test_batch_with_project_to_children_pixel_aspect_propagation(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    project_id = propagation_data.PROJECT_ID
    client = MongoClient()
    populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        propagation_data.AVALON_DATA,
    )
    sg_client = Mock()
    config = batch_config(overwrite=False)
    sg_client.find = sg_query(propagation_data)
    sg_client.find_one = sg_query(propagation_data)
    monkeypatch.setattr(conn, "get_shotgrid_client", fun(sg_client))
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await batch_controller.batch_update(project_id, config)
    # Assert
    assert_that(all_avalon(client)).extracting(
        "data", filter={"type": "asset"}
    ).extracting("pixelAspect").is_equal_to(
        [
            propagation_data.AVALON_DATA[0]["data"].get("pixelAspect")
            for _ in [
                x
                for x in all_avalon(client)
                if x["type"] == AvalonType.ASSET.value
            ]
        ]
    )


@pytest.mark.asyncio
async def test_batch_with_project_to_children_partial_cut_in_propagation(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    project_id = propagation_data.PROJECT_ID
    client = MongoClient()
    populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        propagation_data.AVALON_DATA,
    )
    sg_client = Mock()
    config = batch_config(overwrite=False)
    sg_client.find = sg_query(propagation_data)
    sg_client.find_one = sg_query(propagation_data)
    monkeypatch.setattr(conn, "get_shotgrid_client", fun(sg_client))
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await batch_controller.batch_update(project_id, config)
    # Assert
    assert_that(all_avalon(client)).extracting(
        "data", filter={"name": "SHOT10"}
    ).extracting("clipIn").is_equal_to(
        [propagation_data.SHOTGRID_DATA_SHOTS[0]["sg_cut_in"]]
    )
    assert_that(all_avalon(client)).extracting(
        "data", filter={"name": "Shot"}
    ).extracting("clipIn").is_not_equal_to(
        [propagation_data.SHOTGRID_DATA_SHOTS[0]["sg_cut_in"]]
    )


@pytest.mark.asyncio
async def test_batch_with_project_to_children_partial_cut_out_propagation(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    project_id = propagation_data.PROJECT_ID
    client = MongoClient()
    populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        propagation_data.AVALON_DATA,
    )
    sg_client = Mock()
    config = batch_config(overwrite=False)
    sg_client.find = sg_query(propagation_data)
    sg_client.find_one = sg_query(propagation_data)
    monkeypatch.setattr(conn, "get_shotgrid_client", fun(sg_client))
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await batch_controller.batch_update(project_id, config)
    # Assert
    assert_that(all_avalon(client)).extracting(
        "data", filter={"name": "SHOT10"}
    ).extracting("clipOut").is_equal_to(
        [propagation_data.SHOTGRID_DATA_SHOTS[0]["sg_cut_out"]]
    )
    assert_that(all_avalon(client)).extracting(
        "data", filter={"name": "Shot"}
    ).extracting("clipOut").is_not_equal_to(
        [propagation_data.SHOTGRID_DATA_SHOTS[0]["sg_cut_out"]]
    )
