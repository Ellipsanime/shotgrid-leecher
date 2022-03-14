import uuid
from typing import Dict, Any, List

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from mongomock.mongo_client import MongoClient

from shotgrid_leecher.controller import config_controller
from shotgrid_leecher.record.enums import DbName, DbCollection
from shotgrid_leecher.record.http_models import ShotgridCredentialsModel
from shotgrid_leecher.record.leecher_structures import ShotgridCredentials
from shotgrid_leecher.utils import connectivity as conn
from utils.funcs import (
    fun,
)

Map = Dict[str, Any]


def _all_credentials(client: MongoClient) -> List[Map]:
    return list(
        client.get_database(DbName.LEECHER.value)
        .get_collection(DbCollection.SHOTGRID_CREDENTIALS.value)
        .find({})
    )


def _insert_credentials(client: MongoClient, dic: Map) -> Any:
    return client.get_database(DbName.LEECHER.value).get_collection(
        DbCollection.SHOTGRID_CREDENTIALS.value
    ).insert_one(dic)


@pytest.mark.asyncio
async def test_insert_credentials(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    model = ShotgridCredentialsModel(
        shotgrid_url=f"http://{str(uuid.uuid4())[:5]}.com",
        script_name=str(uuid.uuid4())[:5],
        script_key=str(uuid.uuid4())[:5],
    )
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await config_controller.upsert_credentials(model)

    # Assert
    assert_that(_all_credentials(client)).extracting("_id").is_equal_to(
        [model.shotgrid_url]
    )
    assert_that(_all_credentials(client)).extracting(
        "script_name"
    ).is_equal_to([model.script_name])
    assert_that(_all_credentials(client)).extracting("script_key").is_equal_to(
        [model.script_key]
    )


@pytest.mark.asyncio
async def test_upsert_credentials(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    url = f"http://{str(uuid.uuid4())[:5]}.com"
    _insert_credentials(client, ShotgridCredentials(url, "", "").to_mongo())
    model = ShotgridCredentialsModel(
        shotgrid_url=url,
        script_name=str(uuid.uuid4())[:5],
        script_key=str(uuid.uuid4())[:5],
    )
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await config_controller.upsert_credentials(model)

    # Assert
    assert_that(_all_credentials(client)).extracting("_id").is_equal_to(
        [model.shotgrid_url]
    )
    assert_that(_all_credentials(client)).extracting(
        "script_name"
    ).is_equal_to([model.script_name])
    assert_that(_all_credentials(client)).extracting("script_key").is_equal_to(
        [model.script_key]
    )
