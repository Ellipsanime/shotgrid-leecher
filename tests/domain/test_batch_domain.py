import random
import uuid
from typing import Dict, Any, Callable, List
from unittest.mock import Mock

from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from assertpy.assertpy import AssertionBuilder
from toolz import curry

import shotgrid_leecher.mapper.avalon_mapper as mapper
import shotgrid_leecher.repository.shotgrid_hierarchy_repo as repository
from shotgrid_leecher.domain import batch_domain as sut
from shotgrid_leecher.record.commands import CreateShotgridInAvalonCommand
from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials
from shotgrid_leecher.record.shotgrid_subtypes import (
    FieldsMapping,
    ProjectFieldsMapping,
    AssetFieldsMapping,
    ShotFieldsMapping,
    TaskFieldsMapping,
    StepFieldsMapping,
)
from shotgrid_leecher.writers import db_writer

Map = Dict[str, Any]

TASK_NAMES = ["lines", "color", "look", "dev"]
STEP_NAMES = ["modeling", "shading", "rigging"]


def _fun(param: Any) -> Callable[[Any], Any]:
    return lambda *_: param


def _default_fields_mapping() -> FieldsMapping:
    return FieldsMapping(
        ProjectFieldsMapping.from_dict({}),
        AssetFieldsMapping.from_dict({}),
        ShotFieldsMapping.from_dict({}),
        TaskFieldsMapping.from_dict({}),
        StepFieldsMapping.from_dict({}),
    )


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
    patcher: MonkeyPatch, mapped: Dict, hierarchy: List
) -> None:
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
    _patch_adjacent(monkeypatch, {}, [])
    insert_avalon = Mock(return_value=1)
    monkeypatch.setattr(db_writer, "insert_avalon_row", insert_avalon)
    command = CreateShotgridInAvalonCommand(
        123,
        "",
        ShotgridCredentials("", "", ""),
        _default_fields_mapping(),
    )
    # Act
    sut.create_shotgrid_in_avalon(command)
    # Assert
    assert_that(insert_avalon.called).is_false()


def test_shotgrid_to_avalon_batch_project(monkeypatch: MonkeyPatch):
    # Arrange
    project = _get_project_mapped_rows()
    project_name = project["name"]
    _patch_adjacent(
        monkeypatch,
        {project["name"]: project},
        [{"_id": project["name"]}],
    )
    command = CreateShotgridInAvalonCommand(
        123,
        project_name,
        ShotgridCredentials("", "", ""),
        _default_fields_mapping(),
    )
    insert_avalon = Mock(return_value=1)
    monkeypatch.setattr(db_writer, "insert_avalon_row", insert_avalon)
    # Act
    sut.create_shotgrid_in_avalon(command)
    # Assert
    assert_that([x[0][0] for x in insert_avalon.call_args_list]).is_equal_to(
        [project_name]
    )
    assert_that(insert_avalon.call_args_list[0][0][1]).is_equal_to(
        project,
        ignore=["_id", "data", "parent"],
    )


def test_shotgrid_to_avalon_batch_asset_values(monkeypatch: MonkeyPatch):
    # Arrange
    task_num = 3
    data = _get_simple_asset_mapped_rows(task_num)
    project_name = list(data.keys())[0]
    asset_grp = list(data.keys())[1]
    asset = list(data.keys())[2]
    ids = [project_name, 1, 2]
    _patch_adjacent(monkeypatch, data, [{"_id": project_name}])
    insert_avalon = Mock(side_effect=ids)
    monkeypatch.setattr(db_writer, "insert_avalon_row", insert_avalon)
    command = CreateShotgridInAvalonCommand(
        123,
        project_name,
        ShotgridCredentials("", "", ""),
        _default_fields_mapping(),
    )
    # Act
    sut.create_shotgrid_in_avalon(command)
    # Assert
    assert_that([x[0][0] for x in insert_avalon.call_args_list]).is_equal_to(
        [project_name for _ in range(task_num)]
    )
    assert_that(insert_avalon.call_args_list[0][0][1].get("parent")).is_none()
    assert_that(
        insert_avalon.call_args_list[1][0][1].get("parent")
    ).is_equal_to(project_name)
    assert_that(
        insert_avalon.call_args_list[2][0][1].get("parent")
    ).is_equal_to(project_name)
    assert_that(insert_avalon.call_args_list[1][0][1]).is_equal_to(
        data[asset_grp],
        ignore=["_id", "data"],
    )
    assert_that(insert_avalon.call_args_list[1][0][1].get("data")).is_equal_to(
        data[asset_grp]["data"],
        ignore=["visualParent"],
    )
    assert_that(insert_avalon.call_args_list[2][0][1]).is_equal_to(
        data[asset],
        ignore=["_id", "data"],
    )
    assert_that(insert_avalon.call_args_list[2][0][1].get("data")).is_equal_to(
        data[asset]["data"],
        ignore=["visualParent"],
    )
