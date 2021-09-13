import random
import uuid
from typing import Dict, Any, Callable, List
from unittest.mock import PropertyMock

from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from assertpy.assertpy import AssertionBuilder
from mongomock import MongoClient
from toolz import curry

import shotgrid_leecher.mapper.hierarchy_mapper as mapper
import shotgrid_leecher.repository.shotgrid_hierarchy_repo as repository
import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.domain import batch_domain as sut
from shotgrid_leecher.record.commands import ShotgridToAvalonBatchCommand
from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials

Map = Dict[str, Any]

TASK_NAMES = ["lines", "color", "look", "dev"]
STEP_NAMES = ["modeling", "shading", "rigging"]


def _fun(param: Any) -> Callable[[Any], Any]:
    return lambda *_: param


def _default_avalon_data() -> Map:
    return {
        "clipIn": 1,
        "clipOut": 1,
        "fps": 25.0,
        "frameEnd": 0,
        "frameStart": 0,
        "handleEnd": 0,
        "handleStart": 0,
        "pixelAspect": 0,
        "resolutionHeight": 0,
        "resolutionWidth": 0,
        "tools_env": [],
    }


def _default_avalon_project_data() -> Map:
    data = _default_avalon_data()
    data["code"] = ""
    data["library_project"] = False
    return data


def _default_avalon_asset_data() -> Map:
    data = _default_avalon_data()
    data["parents"] = []
    data["visualParent"] = None
    data["tasks"] = {}
    return data


def _get_project_mapped_rows() -> Dict[str, Any]:
    return {
        "type": "project",
        "name": f"Project_{str(uuid.uuid4())}",
        "data": _default_avalon_project_data(),
        "schema": "openpype:project-3.0",
        "config": {
            "apps": [],
            "imageio": {},
            "roots": {},
            "tasks": {},
            "templates": {},
        },
    }


def _get_simple_asset_mapped_rows(task_num: int) -> Dict[str, Map]:
    project = _get_project_mapped_rows()
    asset_grp = {
        "type": "asset",
        "name": "Asset",
        "data": _default_avalon_asset_data(),
        "schema": "openpype:project-3.0",
        "parent": project["name"],
    }
    asset = {
        "type": "asset",
        "name": f"Fork_{str(uuid.uuid4())}",
        "data": _default_avalon_asset_data(),
        "schema": "openpype:project-3.0",
        "parent": project["name"],
    }
    asset["data"]["visualParent"] = asset_grp["name"]
    asset["data"]["parent"] = [asset_grp["name"]]
    for task in range(task_num):
        step = random.choice(STEP_NAMES)
        asset["data"]["tasks"][
            f"{random.choice(TASK_NAMES)}_{str(uuid.uuid4())}"
        ] = {"type": step}
        if step not in project["config"]["tasks"]:
            project["config"]["tasks"][step] = {}

    return {
        project["name"]: project,
        asset_grp["name"]: asset_grp,
        asset["name"]: asset,
    }


def _patch_adjacent(
    patcher: MonkeyPatch, client, mapped: Dict, hierarchy: List
) -> None:
    patcher.setattr(conn, "get_db_client", _fun(client))
    patcher.setattr(mapper, "shotgrid_to_avalon", _fun(mapped))
    patcher.setattr(repository, "get_hierarchy_by_project", _fun(hierarchy))


@curry
def _assert_db(
    col_getter: Callable, val: Dict, key: str = None
) -> AssertionBuilder:
    if not key:
        return assert_that(col_getter().find_one(val))
    return assert_that(col_getter().find_one(val).get(key))


def test_shotgrid_to_avalon_batch_empty(monkeypatch: MonkeyPatch):
    # Arrange
    client = PropertyMock()
    _patch_adjacent(monkeypatch, client, {}, [])
    command = ShotgridToAvalonBatchCommand(
        123, "", True, ShotgridCredentials("", "", "")
    )
    # Act
    sut.shotgrid_to_avalon(command)
    # Assert
    assert_that(client.get_database.called).is_false()


def test_shotgrid_to_avalon_batch_project(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    project = _get_project_mapped_rows()
    _patch_adjacent(
        monkeypatch,
        client,
        {project["name"]: project},
        [{"_id": project["name"]}],
    )
    command = ShotgridToAvalonBatchCommand(
        123, "", True, ShotgridCredentials("", "", "")
    )
    assert_db = _assert_db(lambda: client["avalon"][project["name"]])
    # Act
    sut.shotgrid_to_avalon(command)
    # Assert
    assert_that(client.list_database_names()).is_equal_to(["avalon"])
    assert_that(client["avalon"].list_collection_names()).is_equal_to(
        [project["name"]]
    )
    assert_db({"name": project["name"]}).is_not_none().contains_key(
        "_id"
    ).is_equal_to(project, ignore="_id")


def test_shotgrid_to_avalon_batch_asset_values(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    task_num = 3
    data = _get_simple_asset_mapped_rows(task_num)
    project_name = list(data.keys())[0]
    asset_grp = list(data.keys())[1]
    asset = list(data.keys())[2]
    _patch_adjacent(monkeypatch, client, data, [{"_id": project_name}])
    command = ShotgridToAvalonBatchCommand(
        123, "", True, ShotgridCredentials("", "", "")
    )
    assert_db = _assert_db(lambda: client["avalon"][project_name])
    # Act
    sut.shotgrid_to_avalon(command)
    # Assert
    assert_that(list(client["avalon"][project_name].find())).is_length(3)
    assert_db({"name": data[asset_grp]["name"]}).is_equal_to(
        data[asset_grp],
        ignore=["_id", "data"],
    )
    assert_db({"name": data[asset_grp]["name"]}, key="data").is_equal_to(
        data[asset_grp]["data"],
        ignore="visualParent",
    )
    assert_db({"name": data[asset]["name"]}).is_equal_to(
        data[asset],
        ignore=["_id", "data"],
    )
    assert_db({"name": data[asset]["name"]}, key="data").is_equal_to(
        data[asset]["data"],
        ignore="visualParent",
    )
