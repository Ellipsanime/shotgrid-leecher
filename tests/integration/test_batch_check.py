from typing import Dict, Any, List, Union
from unittest.mock import Mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from mongomock.mongo_client import MongoClient
from toolz import curry

from asset import fields_mapping_data
from shotgrid_leecher.controller import batch_controller
from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.record.results import BatchCheckResult
from shotgrid_leecher.utils import connectivity as conn
from utils.funcs import (
    fun,
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
