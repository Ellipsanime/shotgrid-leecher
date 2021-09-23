import random
import uuid
from typing import Any, Callable, List
from unittest.mock import Mock

from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from mongomock import MongoClient
from mongomock.object_id import ObjectId

import shotgrid_leecher.repository.shotgrid_hierarchy_repo as repository
import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.domain import batch_domain as sut
from shotgrid_leecher.record.commands import ShotgridToAvalonBatchCommand
from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials
from shotgrid_leecher.repository import hierarchy_repo
from shotgrid_leecher.writers import db_writer

TASK_NAMES = ["lines", "color", "look", "dev"]
STEP_NAMES = ["modeling", "shading", "rigging"]


def _fun(param: Any) -> Callable[[Any], Any]:
    return lambda *_: param


def _patch_adjacent(patcher: MonkeyPatch, client, hierarchy: List) -> None:
    patcher.setattr(conn, "get_db_client", _fun(client))
    patcher.setattr(repository, "get_hierarchy_by_project", _fun(hierarchy))


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
            "src_id": uuid.uuid4().int,
            "type": "Asset",
            "parent": f"{parent['parent']}{parent['_id']},PRP,",
        },
    ]


def _get_prp_asset_with_tasks(parent, task_num):
    asset = _get_prp_asset(parent)
    tasks = [
        {
            "_id": f"{random.choice(TASK_NAMES)}_{uuid.uuid4().int}",
            "src_id": uuid.uuid4().int,
            "type": "Task",
            "task_type": random.choice(STEP_NAMES),
            "parent": f"{asset[1]['parent']}{asset[1]['_id']},",
        }
        for i in range(task_num)
    ]
    return [*asset, *tasks]


def test_shotgrid_to_avalon_batch_update_empty(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    _patch_adjacent(monkeypatch, client, [])
    command = ShotgridToAvalonBatchCommand(
        123, "", True, ShotgridCredentials("", "", "")
    )

    # Act
    sut.update_shotgrid_in_avalon(command)

    # Assert
    assert_that(client["avalon"].list_collection_names()).is_length(0)


def test_shotgrid_to_avalon_batch_update_project(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    data = [_get_project()]
    last_batch_data = [{**x, "object_id": ObjectId()} for x in data]

    upsert_mock = Mock(return_value=last_batch_data[0]["object_id"])
    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(
        hierarchy_repo, "fetch_intermediates", _fun(last_batch_data)
    )
    monkeypatch.setattr(db_writer, "overwrite_hierarchy", _fun(None))
    monkeypatch.setattr(db_writer, "upsert_avalon_row", upsert_mock)

    command = ShotgridToAvalonBatchCommand(
        123, "test", True, ShotgridCredentials("", "", "")
    )

    # Act
    sut.update_shotgrid_in_avalon(command)

    # Assert
    assert_that(upsert_mock.call_args).is_length(2)
    assert_that(upsert_mock.call_args_list).is_length(1)
    assert_that(upsert_mock.call_args_list[0][0][1]["_id"]).is_equal_to(
        last_batch_data[0]["object_id"]
    )


def test_shotgrid_to_avalon_batch_update_asset_value(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    project = _get_project()
    asset_grp = _get_asset_group(project)
    data = [project, asset_grp, *_get_prp_asset(asset_grp)]
    last_batch_data = [{**x, "object_id": ObjectId()} for x in data[:2]]

    call_list = []

    def upsert_mock(project_name, row):
        call_list.append(row)
        return row["_id"]

    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(
        hierarchy_repo, "fetch_intermediates", _fun(last_batch_data)
    )
    monkeypatch.setattr(db_writer, "overwrite_hierarchy", _fun(None))
    monkeypatch.setattr(db_writer, "upsert_avalon_row", upsert_mock)

    command = ShotgridToAvalonBatchCommand(
        123, project["_id"], True, ShotgridCredentials("", "", "")
    )

    # Act
    sut.update_shotgrid_in_avalon(command)

    # Assert
    assert_that(call_list).is_length(4)
    assert_that(call_list[0]["_id"]).is_equal_to(
        last_batch_data[0]["object_id"]
    )
    assert_that(call_list[1]["_id"]).is_equal_to(
        last_batch_data[1]["object_id"]
    )


def test_shotgrid_to_avalon_batch_update_asset_hierarchy_db(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    client = MongoClient()
    project = _get_project()
    asset_grp = _get_asset_group(project)
    data = [project, asset_grp, *_get_prp_asset(asset_grp)]
    last_batch_data = [{**x, "object_id": ObjectId()} for x in data[:2]]

    def upsert_mock(project_name, row):
        return row["_id"]

    insert_intermediate = Mock()

    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(
        hierarchy_repo, "fetch_intermediates", _fun(last_batch_data)
    )
    monkeypatch.setattr(db_writer, "overwrite_hierarchy", insert_intermediate)
    monkeypatch.setattr(db_writer, "upsert_avalon_row", upsert_mock)

    command = ShotgridToAvalonBatchCommand(
        123, project["_id"], True, ShotgridCredentials("", "", "")
    )

    # Act
    sut.update_shotgrid_in_avalon(command)

    # Assert
    assert_that(insert_intermediate.call_count).is_equal_to(1)
    assert_that(insert_intermediate.call_args_list[0][0][1]).is_type_of(list)
    assert_that(
        insert_intermediate.call_args_list[0][0][1][0]["object_id"]
    ).is_equal_to(last_batch_data[0]["object_id"])
    assert_that(
        insert_intermediate.call_args_list[0][0][1][1]["object_id"]
    ).is_equal_to(last_batch_data[1]["object_id"])
    assert_that(insert_intermediate.call_args_list[0][0][1][2]).contains_key(
        "object_id"
    )
    assert_that(insert_intermediate.call_args_list[0][0][1][3]).contains_key(
        "object_id"
    )


def test_shotgrid_to_avalon_batch_update_workfile_upserted_values(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    # Act
    # Assert
    pass


def test_shotgrid_to_avalon_batch_update_asset_with_tasks(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    client = MongoClient()
    project = _get_project()
    asset_grp = _get_asset_group(project)
    data = [project, asset_grp, *_get_prp_asset_with_tasks(asset_grp, 3)]
    last_batch_data = [{**x, "object_id": ObjectId()} for x in data[:4]]
    last_batch_data.append({**data[4], "parent_object_id": ObjectId()})

    call_list = []

    def upsert_mock(project_name, row):
        call_list.append(row)
        return row["_id"]

    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(
        hierarchy_repo, "fetch_intermediates", _fun(last_batch_data)
    )
    monkeypatch.setattr(db_writer, "overwrite_hierarchy", _fun(None))
    monkeypatch.setattr(db_writer, "upsert_avalon_row", upsert_mock)

    command = ShotgridToAvalonBatchCommand(
        123, project["_id"], True, ShotgridCredentials("", "", "")
    )

    # Act
    sut.update_shotgrid_in_avalon(command)

    # Assert
    assert_that(call_list).is_length(4)
    assert_that(call_list[0]["_id"]).is_equal_to(
        last_batch_data[0]["object_id"]
    )
