from typing import Dict, Any, List, Union
from unittest.mock import Mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from mongomock.mongo_client import MongoClient
from toolz import curry

import repository.shotgrid_hierarchy_repo as repository
from asset import fields_mapping_data
from asset import update_values_data
from controller import batch_controller
from mapper import intermediate_mapper
from record.enums import ShotgridType, DbName
from record.results import BatchCheckResult
from utils import connectivity as conn
from utils.funcs import (
    fun,
    all_avalon,
    populate_db,
    batch_config,
)

Map = Dict[str, Any]


@curry
def _sg_query(
    data: List[Dict],
    type_: str,
    filters: List[List[Any]],
    fields: List[str],
) -> Union[List[Map], Map]:
    if type_ == ShotgridType.PROJECT.value:
        return data[0]
    raise RuntimeError(f"Unknown type {type_}")


@pytest.mark.asyncio
async def test_batch_first_level_virtual_orphans(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    project_id = update_values_data.PROJECT_ID
    populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        update_values_data.AVALON_DATA,
    )
    populate_db(
        client.get_database(DbName.INTERMEDIATE.value).get_collection(
            project_id
        ),
        update_values_data.INTERMEDIATE_DB_DATA,
    )
    monkeypatch.setattr(
        repository,
        "get_hierarchy_by_project",
        Mock(
            return_value=intermediate_mapper.map_parent_ids(
                [
                    intermediate_mapper.to_row(x)
                    for x in update_values_data.SHOTGRID_DATA
                ]
            )
        ),
    )
    monkeypatch.setattr(conn, "get_db_client", fun(client))

    # Act
    await batch_controller.batch_update(project_id, batch_config())

    # Assert
    assert_that(all_avalon(client)).is_length(
        len(update_values_data.AVALON_DATA)
    )
    assert_that(all_avalon(client)).extracting(
        "data", filter={"name": "Asset"}
    ).extracting("visualParent").is_equal_to([None])
    assert_that(all_avalon(client)).extracting("data").extracting(
        "visualParent", filter=lambda x: x["visualParent"]
    ).is_length(len(update_values_data.AVALON_DATA) - 2)


@pytest.mark.asyncio
async def test_batch_check(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    sg_client = Mock()
    project = {**fields_mapping_data.SHOTGRID_DATA_PROJECT[0], "id": 123}
    sg_client.find_one = _sg_query([project])
    monkeypatch.setattr(conn, "get_shotgrid_client", fun(sg_client))
    monkeypatch.setattr(conn, "get_db_client", fun(client))

    # Act
    actual = await batch_controller.batch_check(
        "http://google.com",
        123,
        "1",
        "1",
    )

    # Assert
    assert_that(BatchCheckResult(**actual)).is_equal_to(
        BatchCheckResult(project["name"])
    )
