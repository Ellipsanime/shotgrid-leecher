from typing import Dict, Any, List
from unittest.mock import Mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from bson import ObjectId
from mongomock.mongo_client import MongoClient

from asset import fields_mapping_data
from controller import batch_controller
from record.avalon_structures import (
    AvalonProject,
    AvalonProjectData,
)
from record.enums import ShotgridType
from record.http_models import BatchConfig
from repository import avalon_repo
from utils import connectivity as conn
from utils.funcs import (
    batch_config,
    avalon_collections,
    fun,
    intermediate_collections,
    all_intermediate,
    sg_query,
)

Map = Dict[str, Any]


def _batch_config(fields_mapping: Dict, overwrite=True) -> BatchConfig:
    return batch_config(overwrite).copy(
        update={"fields_mapping": fields_mapping}
    )


def _extract(field: str, data: List[Dict]) -> List[Any]:
    return [x.get(field) for x in data]


@pytest.mark.asyncio
async def test_batch_with_fields_mapping(monkeypatch: MonkeyPatch):
    # Arrange
    project_id = fields_mapping_data.PROJECT_ID
    fields_mapping = fields_mapping_data.FIELDS_MAPPING
    client = MongoClient()
    sg_client = Mock()
    sg_client.find = sg_query(fields_mapping_data)
    sg_client.find_one = sg_query(fields_mapping_data)
    project = AvalonProject(
        str(ObjectId()),
        project_id,
        AvalonProjectData(),
        dict(),
    )
    monkeypatch.setattr(avalon_repo, "fetch_project", fun(project))
    monkeypatch.setattr(conn, "get_shotgrid_client", fun(sg_client))
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await batch_controller.batch_update(
        project_id, _batch_config(fields_mapping)
    )

    # Assert
    assert_that(avalon_collections(client)).is_length(1)
    assert_that(intermediate_collections(client)).is_length(1)
    assert_that(all_intermediate(client)).extracting(
        "src_id", filter={"type": ShotgridType.PROJECT.value}
    ).is_equal_to(
        _extract(
            fields_mapping_data.FIELD_PROJECT_ID,
            fields_mapping_data.SHOTGRID_DATA_PROJECT,
        )
    )
    assert_that(all_intermediate(client)).extracting(
        "src_id", filter={"type": ShotgridType.ASSET.value}
    ).is_equal_to(
        _extract(
            fields_mapping_data.FIELD_ASSET_ID,
            fields_mapping_data.SHOTGRID_DATA_ASSETS,
        )
    )
    assert_that(all_intermediate(client)).extracting(
        "_id", filter={"parent": f",{project_id},{ShotgridType.ASSET.value},"}
    ).is_equal_to(
        _extract(
            fields_mapping_data.FIELD_ASSET_TYPE,
            fields_mapping_data.SHOTGRID_DATA_ASSETS,
        )
    )
    assert_that(all_intermediate(client)).extracting(
        "src_id", filter={"type": ShotgridType.TASK.value}
    ).is_equal_to(
        _extract(
            fields_mapping_data.FIELD_TASK_ID,
            fields_mapping_data.SHOTGRID_DATA_TASKS,
        )
    )