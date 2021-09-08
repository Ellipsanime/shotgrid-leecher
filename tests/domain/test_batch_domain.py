import random
import uuid
from typing import Dict, Any
from unittest.mock import PropertyMock, patch

from assertpy import assert_that
from mongomock import MongoClient

from shotgrid_leecher.domain import batch_domain as sut
from shotgrid_leecher.domain.batch_domain import ShotgridToAvalonBatchCommand

Map = Dict[str, Any]

TASK_NAMES = ["lines", "color", "look", "dev"]
STEP_NAMES = ["modeling", "shading", "rigging"]


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


@patch("shotgrid_leecher.repository.shotgrid_hierarchy_repo")
@patch("shotgrid_leecher.utils.connectivity.get_shotgrid_client")
@patch("shotgrid_leecher.utils.connectivity.ShotgridClient")
@patch("shotgrid_leecher.mapper.hierarchy_mapper.shotgrid_to_avalon")
@patch("shotgrid_leecher.utils.connectivity.get_db_client")
def test_shotgrid_to_avalon_batch_empty(
    get_mongo: PropertyMock,
    shotgrid_to_avalon: PropertyMock,
    *_: PropertyMock,
):
    # Arrange
    client = PropertyMock()
    get_mongo.return_value = client
    shotgrid_to_avalon.return_value = {}
    command = ShotgridToAvalonBatchCommand(123, True)
    # Act
    sut.shotgrid_to_avalon(command)
    # Assert
    assert_that(client.get_database.called).is_false()


@patch("shotgrid_leecher.utils.connectivity.ShotgridClient")
@patch("shotgrid_leecher.utils.connectivity.get_shotgrid_client")
@patch("shotgrid_leecher.mapper.hierarchy_mapper.shotgrid_to_avalon")
@patch(
    "shotgrid_leecher.repository.shotgrid_hierarchy_repo"
    ".get_hierarchy_by_project"
)
@patch("shotgrid_leecher.utils.connectivity.get_db_client")
def test_shotgrid_to_avalon_batch_project(
    get_mongo: PropertyMock,
    repo: PropertyMock,
    shotgrid_to_avalon: PropertyMock,
    *_: PropertyMock,
):
    # Arrange
    client = MongoClient()
    get_mongo.return_value = client
    project = _get_project_mapped_rows()
    repo.return_value = [{"_id": project["name"]}]
    shotgrid_to_avalon.return_value = {project["name"]: project}
    command = ShotgridToAvalonBatchCommand(123, True)
    # Act
    sut.shotgrid_to_avalon(command)
    # Assert
    assert_that(client.list_database_names()).is_equal_to(["avalon"])
    assert_that(client["avalon"].list_collection_names()).is_equal_to(
        [project["name"]]
    )
    assert_that(
        client["avalon"][project["name"]].find_one({"name": project["name"]})
    ).is_not_none().contains_key("_id").is_equal_to(project, ignore="_id")


@patch("shotgrid_leecher.utils.connectivity.ShotgridClient")
@patch("shotgrid_leecher.utils.connectivity.get_shotgrid_client")
@patch("shotgrid_leecher.mapper.hierarchy_mapper.shotgrid_to_avalon")
@patch(
    "shotgrid_leecher.repository.shotgrid_hierarchy_repo"
    ".get_hierarchy_by_project"
)
@patch("shotgrid_leecher.utils.connectivity.get_db_client")
def test_shotgrid_to_avalon_batch_asset_values(
    get_mongo: PropertyMock,
    repo: PropertyMock,
    shotgrid_to_avalon: PropertyMock,
    *_: PropertyMock,
):
    # Arrange
    client = MongoClient()
    task_num = 3
    get_mongo.return_value = client
    data = _get_simple_asset_mapped_rows(task_num)
    project_name = list(data.keys())[0]
    asset_grp = list(data.keys())[1]
    asset = list(data.keys())[2]
    repo.return_value = [{"_id": project_name}]
    shotgrid_to_avalon.return_value = data
    command = ShotgridToAvalonBatchCommand(123, True)
    # Act
    sut.shotgrid_to_avalon(command)
    # Assert
    assert_that(list(client["avalon"][project_name].find())).is_length(3)
    assert_that(
        client["avalon"][project_name].find_one(
            {"name": data[asset_grp]["name"]}
        )
    ).is_equal_to(data[asset_grp], ignore=["_id", "data"])
    assert_that(
        client["avalon"][project_name].find_one(
            {"name": data[asset_grp]["name"]}
        )['data']
    ).is_equal_to(data[asset_grp]["data"], ignore="visualParent")
    assert_that(
        client["avalon"][project_name].find_one(
            {"name": data[asset]["name"]}
        )
    ).is_equal_to(data[asset], ignore=["_id", "data"])
    assert_that(
        client["avalon"][project_name].find_one(
            {"name": data[asset]["name"]}
        )['data']
    ).is_equal_to(data[asset]["data"], ignore="visualParent")
