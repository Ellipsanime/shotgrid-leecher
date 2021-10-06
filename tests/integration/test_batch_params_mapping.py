from typing import Dict, Any, Callable, List, Union
from unittest.mock import Mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from mongomock.mongo_client import MongoClient
from toolz import curry

from asset import params_data
from shotgrid_leecher.controller import batch_controller
from shotgrid_leecher.record.enums import DbName, ShotgridType
from shotgrid_leecher.record.http_models import BatchConfig
from shotgrid_leecher.utils import connectivity as conn

Map = Dict[str, Any]


def _fun(param: Any) -> Callable[[Any], Any]:
    return lambda *_: param


def _batch_config(overwrite=True) -> BatchConfig:
    return BatchConfig(
        shotgrid_project_id=123,
        overwrite=overwrite,
        shotgrid_url="http://google.com",
        script_name="1",
        script_key="1",
        fields_mapping={},
    )


def _avalon_collections(client: MongoClient) -> List[str]:
    return client.get_database(DbName.AVALON.value).list_collection_names()


def _intermediate_collections(client: MongoClient) -> List[str]:
    return client.get_database(
        DbName.INTERMEDIATE.value
    ).list_collection_names()


def _all_avalon(client: MongoClient) -> List[Map]:
    col = client.get_database(DbName.AVALON.value).list_collection_names()[0]
    return list(
        client.get_database(DbName.AVALON.value).get_collection(col).find({})
    )


def _all_intermediate(client: MongoClient) -> List[Map]:
    col = client.get_database(
        DbName.INTERMEDIATE.value
    ).list_collection_names()[0]
    return list(
        client.get_database(DbName.INTERMEDIATE.value)
        .get_collection(col)
        .find({})
    )


@curry
def _sg_query(
    data: Any,
    type_: str,
    filters: List[List[Any]],
    fields: List[str],
) -> Union[List[Map], Map]:
    if type_ == ShotgridType.PROJECT.value:
        return data.SHOTGRID_DATA_PROJECT[0]
    if type_ == ShotgridType.ASSET.value:
        return data.SHOTGRID_DATA_ASSETS
    if type_ == ShotgridType.SHOT.value:
        return data.SHOTGRID_DATA_SHOTS
    if type_ == ShotgridType.TASK.value:
        return data.SHOTGRID_DATA_TASKS
    raise RuntimeError(f"Unknown type {type_}")


def _extract(field: str, data: List[Dict]) -> List[Any]:
    return [x.get(field) for x in data]


@pytest.mark.asyncio
async def test_batch_with_params(monkeypatch: MonkeyPatch):
    # Arrange
    project_id = params_data.PROJECT_ID
    client = MongoClient()
    sg_client = Mock()
    sg_client.find = _sg_query(params_data)
    sg_client.find_one = _sg_query(params_data)
    monkeypatch.setattr(conn, "get_shotgrid_client", _fun(sg_client))
    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    # Act
    await batch_controller.batch(project_id, _batch_config())

    # Assert
    assert_that(_avalon_collections(client)).is_length(1)
    assert_that(_intermediate_collections(client)).is_length(1)
    # assert_that(_all_avalon(client)).is_length(1)
    # assert_that(_all_intermediate(client)).is_length(1)
