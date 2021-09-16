import uuid
from typing import Any, Callable, List
from unittest.mock import Mock

from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from mongomock import MongoClient

import shotgrid_leecher.utils.connectivity as conn
import shotgrid_leecher.repository.shotgrid_hierarchy_repo as repository
from shotgrid_leecher.domain import batch_domain as sut
from shotgrid_leecher.record.commands import ShotgridToAvalonBatchCommand
from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials

TASK_NAMES = ["lines", "color", "look", "dev"]
STEP_NAMES = ["modeling", "shading", "rigging"]


def _fun(param: Any) -> Callable[[Any], Any]:
    return lambda *_: param


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
            "src_id": uuid.uuid4().int & (1 << 16) - 1,
            "type": "Asset",
            "parent": f"{parent['parent']}{parent['_id']},PRP,",
        },
    ]


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
        123, project['_id'], True, ShotgridCredentials("", "", "")
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
        123, project['_id'], True, ShotgridCredentials("", "", "")
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
    asset_updated['_id'] = "Knife"

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
