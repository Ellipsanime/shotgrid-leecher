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
from shotgrid_leecher.domain.batch_domain import InsertMongoAvalon
from shotgrid_leecher.record.commands import ShotgridToAvalonBatchCommand
from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials

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
    sut.batch_update_shotgrid_to_avalon(command)

    # Assert
    assert_that(client["avalon"].list_collection_names()).is_length(0)


def test_shotgrid_to_avalon_batch_update_project(monkeypatch: MonkeyPatch):
    # Arrange
    data = [_get_project()]
    last_batch_data = [{**x, "oid": ObjectId()} for x in data]

    upsert_mock = Mock(return_value=last_batch_data[0]["oid"])
    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(
        InsertMongoAvalon, "get_last_intermediate_rows", _fun(last_batch_data)
    )
    monkeypatch.setattr(
        InsertMongoAvalon, "insert_intermediate_rows", _fun(None)
    )
    monkeypatch.setattr(InsertMongoAvalon, "upsert_in_avalon", upsert_mock)

    command = ShotgridToAvalonBatchCommand(
        123, "", True, ShotgridCredentials("", "", "")
    )

    # Act
    sut.batch_update_shotgrid_to_avalon(command)

    # Assert
    assert_that(upsert_mock.call_args).is_length(2)
    assert_that(upsert_mock.call_args_list).is_length(1)
    assert_that(upsert_mock.call_args_list[0][0][1]["_id"]).is_equal_to(
        last_batch_data[0]["oid"]
    )


def test_shotgrid_to_avalon_batch_update_asset_value(monkeypatch: MonkeyPatch):
    # Arrange
    project = _get_project()
    asset_grp = _get_asset_group(project)
    data = [project, asset_grp, *_get_prp_asset(asset_grp)]
    last_batch_data = [{**x, "oid": ObjectId()} for x in data[:2]]

    call_list = []

    def upsert_mock(a, project_name, row):
        call_list.append(row)
        return row["_id"]

    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(
        InsertMongoAvalon, "get_last_intermediate_rows", _fun(last_batch_data)
    )
    monkeypatch.setattr(
        InsertMongoAvalon, "insert_intermediate_rows", _fun(None)
    )
    monkeypatch.setattr(InsertMongoAvalon, "upsert_in_avalon", upsert_mock)

    command = ShotgridToAvalonBatchCommand(
        123, "", True, ShotgridCredentials("", "", "")
    )

    # Act
    sut.batch_update_shotgrid_to_avalon(command)

    # Assert
    assert_that(call_list).is_length(4)
    assert_that(call_list[0]["_id"]).is_equal_to(last_batch_data[0]["oid"])
    assert_that(call_list[1]["_id"]).is_equal_to(last_batch_data[1]["oid"])


def test_shotgrid_to_avalon_batch_update_asset_db(monkeypatch: MonkeyPatch):
    # Arrange
    project = _get_project()
    asset_grp = _get_asset_group(project)
    data = [project, asset_grp, *_get_prp_asset(asset_grp)]
    last_batch_data = [{**x, "oid": ObjectId()} for x in data[:2]]

    def upsert_mock(a, project_name, row):
        return row["_id"]

    insert_intermediate = Mock()

    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(
        InsertMongoAvalon, "get_last_intermediate_rows", _fun(last_batch_data)
    )
    monkeypatch.setattr(
        InsertMongoAvalon, "insert_intermediate_rows", insert_intermediate
    )
    monkeypatch.setattr(InsertMongoAvalon, "upsert_in_avalon", upsert_mock)

    command = ShotgridToAvalonBatchCommand(
        123, "", True, ShotgridCredentials("", "", "")
    )

    # Act
    sut.batch_update_shotgrid_to_avalon(command)

    # Assert
    assert_that(insert_intermediate.call_count).is_equal_to(1)
    assert_that(insert_intermediate.call_args_list[0][0][1]).is_type_of(list)
    assert_that(
        insert_intermediate.call_args_list[0][0][1][0]["oid"]
    ).is_equal_to(last_batch_data[0]["oid"])
    assert_that(
        insert_intermediate.call_args_list[0][0][1][1]["oid"]
    ).is_equal_to(last_batch_data[1]["oid"])
    assert_that(insert_intermediate.call_args_list[0][0][1][2]).contains_key(
        "oid"
    )
    assert_that(insert_intermediate.call_args_list[0][0][1][3]).contains_key(
        "oid"
    )
