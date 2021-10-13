import random
import uuid
from typing import Dict, Any, Callable, List

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from mongomock.mongo_client import MongoClient

from shotgrid_leecher.controller import schedule_controller
from shotgrid_leecher.record.enums import DbName
from shotgrid_leecher.record.http_models import BatchConfig
from shotgrid_leecher.utils import connectivity as conn

Map = Dict[str, Any]


def _fun(param: Any) -> Callable[[Any], Any]:
    return lambda *_: param


def _all_db(client: MongoClient) -> List[Map]:
    col = client.get_database(DbName.SCHEDULE.value).list_collection_names()[0]
    return list(
        client.get_database(DbName.SCHEDULE.value).get_collection(col).find({})
    )


def _batch_config() -> BatchConfig:
    return BatchConfig(
        shotgrid_project_id=random.randint(10 ** 2, 10 ** 5),
        shotgrid_url=f"http://{uuid.uuid4()}.com",
        script_name=str(uuid.uuid4()),
        script_key=str(uuid.uuid4()),
        fields_mapping={},
    )


@pytest.mark.asyncio
async def test_schedule_batch(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    project_name = f"project_{str(uuid.uuid4())[:5]}"
    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    # Act
    config = _batch_config()
    await schedule_controller.schedule_batch(project_name, config)

    # Assert
    assert_that(_all_db(client)).extracting("_id").is_equal_to([project_name])
    assert_that(_all_db(client)).extracting("command").extracting(
        "project_id"
    ).is_equal_to([config.shotgrid_project_id])
    assert_that(_all_db(client)).extracting("command").extracting(
        "credentials"
    ).extracting("shotgrid_url").is_equal_to([config.shotgrid_url])
