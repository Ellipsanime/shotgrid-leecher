import uuid
import random
from typing import Any, Dict, Callable, List
from unittest.mock import Mock

from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from mongomock import MongoClient, ObjectId

import shotgrid_leecher.utils.connectivity as conn
import shotgrid_leecher.repository.shotgrid_hierarchy_repo as repository
from shotgrid_leecher.domain import batch_domain as sut
from shotgrid_leecher.record.commands import ShotgridToAvalonBatchCommand
from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials

TASK_NAMES = ["lines", "color", "look", "dev"]
STEP_NAMES = ["modeling", "shading", "rigging"]

Map = Dict[str, Any]


def _fun(param: Any) -> Callable[[Any], Any]:
    return lambda *_: param


def _generate_shotgrid_id() -> int:
    return uuid.uuid4().int & (1 << 16) - 1


def _get_project():

    project_id = str(uuid.uuid4())[0:8]
    return {
        "_id": f"Project_{project_id}",
        "src_id": 111,
        "type": "Project",
        "parent": None,
    }


def _get_asset_group(project):

    return {"_id": "Asset", "type": "Group", "parent": f",{project['_id']},"}


def _get_shot_group(project):

    return {"_id": "Shot", "type": "Group", "parent": f",{project['_id']},"}


def _get_prp_asset(parent):

    return [
        {
            "_id": "PRP",
            "type": "Group",
            "parent": f"{parent['parent']}{parent['_id']},",
        },
        {
            "_id": "Fork",
            "src_id": _generate_shotgrid_id(),
            "type": "Asset",
            "parent": f"{parent['parent']}{parent['_id']},PRP,",
        },
    ]


def _get_prp_asset_with_tasks(parent, task_num):
    asset = _get_prp_asset(parent)
    tasks = [
        {
            "_id": f"{random.choice(TASK_NAMES)}_{uuid.uuid4().int}",
            "src_id": _generate_shotgrid_id(),
            "type": "Task",
            "task_type": random.choice(STEP_NAMES),
            "parent": f"{asset[1]['parent']}{asset[1]['_id']},",
        }
        for i in range(task_num)
    ]
    return [*asset, *tasks]


def _create_avalon_project_row(project_name: str) -> Map:
    return {
        "_id": ObjectId(),
        "type": "project",
        "name": project_name,
        "schema": "openpype:project-3.0",
        "config": {
            "apps": [{"name": "maya/2020"}],
            "imageio": {"hiero": {"workfile": {"logLut": "Cineon"}}},
            "roots": {"windows": "C:/projects"},
            "templates": {"default": {}},
        },
    }


def test_update_shotgrid_to_avalon_empty(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    data: List[Any] = []

    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    command = ShotgridToAvalonBatchCommand(
        123, "", True, ShotgridCredentials("", "", "")
    )

    # Act
    sut.batch_update_shotgrid_to_avalon(command)

    # Assert
    assert_that(client.list_database_names()).is_length(0)


def test_update_shotgrid_to_avalon_init_project(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    project = _get_project()
    data = [project]

    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    command = ShotgridToAvalonBatchCommand(
        123, project["_id"], True, ShotgridCredentials("", "", "")
    )

    # Act
    sut.batch_update_shotgrid_to_avalon(command)

    # Assert
    assert_that(client.list_database_names()).is_length(2)
    assert_that(client.list_database_names()).is_equal_to(
        ["shotgrid_openpype", "avalon"]
    )
    assert_that(
        client.get_database("avalon").list_collection_names()
    ).is_length(1)
    assert_that(
        client.get_database("avalon").list_collection_names()
    ).is_equal_to([project["_id"]])
    assert_that(
        client.get_database("shotgrid_openpype").list_collection_names()
    ).is_length(1)
    assert_that(
        client.get_database("shotgrid_openpype").list_collection_names()
    ).is_equal_to([project["_id"]])


def test_update_shotgrid_to_avalon_update_project(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    project = _get_project()
    data = [project]

    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    command = ShotgridToAvalonBatchCommand(
        123, project["_id"], False, ShotgridCredentials("", "", "")
    )

    project_avalon_init_data = _create_avalon_project_row(project["_id"])
    client.get_database("avalon").get_collection(project["_id"]).insert_one(
        project_avalon_init_data
    )
    # Act
    sut.batch_update_shotgrid_to_avalon(command)

    # Assert
    assert_that(
        list(
            client.get_database("avalon")
            .get_collection(project["_id"])
            .find({})
        )
    ).is_length(1)
    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"type": "project"})
    ).is_not_none()
    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"type": "project"})["config"]
    ).is_type_of(dict)
    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"type": "project"})["config"]
    ).contains_key("apps", "imageio", "roots", "tasks", "templates")
    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"type": "project"})["config"]["apps"]
    ).is_equal_to(project_avalon_init_data["config"]["apps"])
    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"type": "project"})["config"]["imageio"]
    ).is_equal_to(project_avalon_init_data["config"]["imageio"])
    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"type": "project"})["config"]["roots"]
    ).is_equal_to(project_avalon_init_data["config"]["roots"])
    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"type": "project"})["config"]["templates"]
    ).is_equal_to(project_avalon_init_data["config"]["templates"])


def test_update_shotgrid_to_avalon_update_project_tasks(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    task_num = 3
    client = MongoClient()
    project = _get_project()
    asset_grp = _get_asset_group(project)
    asset_and_type = _get_prp_asset_with_tasks(asset_grp, task_num)
    data = [project, asset_grp, *asset_and_type]

    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    command = ShotgridToAvalonBatchCommand(
        123, project["_id"], False, ShotgridCredentials("", "", "")
    )

    project_avalon_init_data = _create_avalon_project_row(project["_id"])
    client.get_database("avalon").get_collection(project["_id"]).insert_one(
        project_avalon_init_data
    )
    # Act
    sut.batch_update_shotgrid_to_avalon(command)

    # Assert
    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"type": "project"})["config"]
    ).contains_key("tasks")
    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"type": "project"})["config"]["tasks"]
        .keys()
    ).contains(*[x["task_type"] for x in asset_and_type[2:]])


def test_update_shotgrid_to_avalon_init_asset(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    project = _get_project()
    asset_grp = _get_asset_group(project)
    asset_and_type = _get_prp_asset(asset_grp)
    data = [project, asset_grp, *asset_and_type]

    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    command = ShotgridToAvalonBatchCommand(
        123, project["_id"], True, ShotgridCredentials("", "", "")
    )

    # Act
    sut.batch_update_shotgrid_to_avalon(command)

    # Assert
    assert_that(
        list(
            client.get_database("avalon")
            .get_collection(project["_id"])
            .find({})
        )
    ).is_length(4)

    assert_that(
        list(
            client.get_database("avalon")
            .get_collection(project["_id"])
            .find({"type": "project"})
        )
    ).is_length(1)

    assert_that(
        list(
            client.get_database("avalon")
            .get_collection(project["_id"])
            .find({"type": "asset"})
        )
    ).is_length(3)

    assert_that(
        list(
            client.get_database("shotgrid_openpype")
            .get_collection(project["_id"])
            .find({})
        )
    ).is_length(len(data))

    assert_that(
        [
            {k: v for (k, v) in x.items() if k != "object_id"}
            for x in list(
                client.get_database("shotgrid_openpype")
                .get_collection(project["_id"])
                .find({})
            )
        ]
    ).is_equal_to(data)


def test_update_shotgrid_to_avalon_overwrite(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    project = _get_project()
    asset_grp = _get_asset_group(project)
    asset_and_type = _get_prp_asset(asset_grp)
    predata = [project, asset_grp, *asset_and_type]

    data = [_get_project()]

    mockdata = Mock()
    mockdata.side_effect = [predata, data]

    monkeypatch.setattr(repository, "get_hierarchy_by_project", mockdata)
    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    command = ShotgridToAvalonBatchCommand(
        123, project["_id"], True, ShotgridCredentials("", "", "")
    )
    sut.batch_update_shotgrid_to_avalon(command)

    # Act
    sut.batch_update_shotgrid_to_avalon(command)

    # Assert
    assert_that(
        client.get_database("avalon").list_collection_names()
    ).is_length(1)
    assert_that(
        list(
            client.get_database("avalon")
            .get_collection(project["_id"])
            .find({})
        )
    ).is_length(1)
    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find({})[0]["type"]
    ).is_equal_to("project")
    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find({})[0]["name"]
    ).is_equal_to(data[0]["_id"])


def test_update_shotgrid_to_avalon_update_values(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    project = _get_project()
    asset_grp = _get_asset_group(project)
    asset_prp, asset = _get_prp_asset(asset_grp)
    asset_updated = dict(asset)
    asset_updated["_id"] = "Knife"

    predata = [project, asset_grp, asset_prp, asset]
    data = [project, asset_grp, asset_prp, asset_updated]

    mockdata = Mock()
    mockdata.side_effect = [predata, data]

    monkeypatch.setattr(repository, "get_hierarchy_by_project", mockdata)
    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    command = ShotgridToAvalonBatchCommand(
        123, project["_id"], True, ShotgridCredentials("", "", "")
    )
    sut.batch_update_shotgrid_to_avalon(command)

    avalon_project_mid_id = (
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"name": project["_id"]})["_id"]
    )
    avalon_asset_grp_mid_id = (
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"name": "Asset"})["_id"]
    )
    avalon_asset_prp_mid_id = (
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"name": "PRP"})["_id"]
    )
    avalon_asset_mid_id = (
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"name": "Fork"})["_id"]
    )
    # Act
    sut.batch_update_shotgrid_to_avalon(command)

    # Assert
    assert_that(
        list(
            client.get_database("avalon")
            .get_collection(project["_id"])
            .find({})
        )
    ).is_length(4)
    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"name": project["_id"]})["_id"]
    ).is_equal_to(avalon_project_mid_id)
    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"name": "Asset"})["_id"]
    ).is_equal_to(avalon_asset_grp_mid_id)
    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"name": "PRP"})["_id"]
    ).is_equal_to(avalon_asset_prp_mid_id)
    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"name": "Knife"})["_id"]
    ).is_equal_to(avalon_asset_mid_id)


def test_update_shotgrid_to_avalon_update_asset_type(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    project = _get_project()
    asset_grp = _get_asset_group(project)
    asset_and_type = _get_prp_asset(asset_grp)
    predata = [project, asset_grp, *asset_and_type]

    asset_type = dict(predata[2])
    asset_type["_id"] = "PROPS"
    asset = dict(predata[3])
    asset["parent"] = f",{project['_id']},Asset,PROPS,"
    data = [project, asset_grp, asset_type, asset]

    mockdata = Mock()
    mockdata.side_effect = [predata, data]

    monkeypatch.setattr(repository, "get_hierarchy_by_project", mockdata)
    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    command = ShotgridToAvalonBatchCommand(
        123, project["_id"], False, ShotgridCredentials("", "", "")
    )
    sut.batch_update_shotgrid_to_avalon(command)

    avalon_asset_mid_id = (
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"name": "Fork"})["_id"]
    )

    # Act
    sut.batch_update_shotgrid_to_avalon(command)

    # Assert
    assert_that(
        list(
            client.get_database("avalon")
            .get_collection(project["_id"])
            .find({})
        )
    ).is_length(5)

    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"name": "Fork"})["_id"]
    ).is_equal_to(avalon_asset_mid_id)

    assert_that(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"name": "Fork"})["data"]["visualParent"]
    ).is_equal_to(
        client.get_database("avalon")
        .get_collection(project["_id"])
        .find_one({"name": "PROPS"})["_id"]
    )
