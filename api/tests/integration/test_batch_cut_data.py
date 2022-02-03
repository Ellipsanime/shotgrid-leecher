from typing import Dict, Any, List
from unittest.mock import Mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from bson import ObjectId
from mongomock.mongo_client import MongoClient

from asset import params_data
from controller import batch_controller
from record.avalon_structures import (
    AvalonProject,
    AvalonProjectData,
)
from record.enums import DbName, ShotgridType
from repository import avalon_repo
from utils import connectivity as conn
from utils.funcs import (
    sg_query,
    batch_config,
    fun,
    all_avalon_by_type,
)

Map = Dict[str, Any]


def _all_intermediate_by_type(
    client: MongoClient, type_: ShotgridType
) -> List[Map]:
    col = client.get_database(
        DbName.INTERMEDIATE.value
    ).list_collection_names()[0]
    return list(
        client.get_database(DbName.INTERMEDIATE.value)
        .get_collection(col)
        .find({"type": type_.value})
    )


def _extract(field: str, data: List[Dict]) -> List[Any]:
    return [x.get(field) for x in data]


@pytest.mark.asyncio
async def test_batch_cut_data_at_intermediate_lvl(monkeypatch: MonkeyPatch):
    # Arrange
    def exp_filter(x):
        params = x.get("params", dict())
        return params.get("clip_in") or params.get("clip_out")

    project_id = params_data.PROJECT_ID
    client = MongoClient()
    sg_client = Mock()
    sg_client.find = sg_query(params_data)
    sg_client.find_one = sg_query(params_data)
    project = AvalonProject(
        str(ObjectId()),
        project_id,
        AvalonProjectData(clip_in=None, clip_out=None),
        {"tasks": {x: {"short_name": x[:1]} for x in ["render"]}},
    )
    monkeypatch.setattr(avalon_repo, "fetch_project", fun(project))
    monkeypatch.setattr(conn, "get_shotgrid_client", fun(sg_client))
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await batch_controller.batch_update(project_id, batch_config())

    # Assert
    assert_that(
        _all_intermediate_by_type(client, ShotgridType.SHOT)
    ).extracting("src_id", filter=exp_filter).is_equal_to(
        _extract(
            "id",
            [
                x
                for x in params_data.SHOTGRID_DATA_SHOTS
                if x.get("sg_cut_in") or x.get("sg_cut_out")
            ],
        )
    )
    assert_that(
        _all_intermediate_by_type(client, ShotgridType.SHOT)
    ).extracting(
        "params", filter=lambda x: x.get("params", dict()).get("clip_in")
    ).extracting(
        "clip_in"
    ).is_equal_to(
        _extract(
            "sg_cut_in",
            [x for x in params_data.SHOTGRID_DATA_SHOTS if x.get("sg_cut_in")],
        )
    )
    assert_that(
        _all_intermediate_by_type(client, ShotgridType.SHOT)
    ).extracting(
        "params", filter=lambda x: x.get("params", dict()).get("clip_out")
    ).extracting(
        "clip_out"
    ).is_equal_to(
        _extract(
            "sg_cut_out",
            [
                x
                for x in params_data.SHOTGRID_DATA_SHOTS
                if x.get("sg_cut_out")
            ],
        )
    )


@pytest.mark.asyncio
async def test_batch_cut_data_at_avalon_lvl(monkeypatch: MonkeyPatch):
    # Arrange
    project_id = params_data.PROJECT_ID
    client = MongoClient()
    sg_client = Mock()
    sg_client.find = sg_query(params_data)
    sg_client.find_one = sg_query(params_data)
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
    await batch_controller.batch_update(project_id, batch_config())

    # Assert
    assert_that(all_avalon_by_type(client, "asset")).extracting(
        "data", filter=lambda x: (x["data"].get("clipIn") or 0) > 10
    ).extracting("clipIn").is_equal_to(
        [
            x["sg_cut_in"]
            for x in params_data.SHOTGRID_DATA_SHOTS
            if "sg_cut_in" in x and x["sg_cut_in"]
        ],
    )
    assert_that(all_avalon_by_type(client, "asset")).extracting(
        "data", filter=lambda x: (x["data"].get("clipOut") or 0) > 10
    ).extracting("clipOut").is_equal_to(
        [
            x["sg_cut_out"]
            for x in params_data.SHOTGRID_DATA_SHOTS
            if "sg_cut_out" in x and x["sg_cut_out"]
        ],
    )
