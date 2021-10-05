import random
import uuid
from typing import Any, Dict, Callable, List
from unittest.mock import Mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from mongomock import MongoClient, ObjectId
from mongomock.collection import Collection

import shotgrid_leecher.repository.shotgrid_hierarchy_repo as repository
import shotgrid_leecher.utils.connectivity as conn
from asset import (
    overwrite_data,
    update_values_data,
    update_asset_data,
    delete_asset_data,
)
from shotgrid_leecher.controller import batch_controller
from shotgrid_leecher.record.enums import DbName
from shotgrid_leecher.record.http_models import BatchConfig
from shotgrid_leecher.utils import generator

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


def _batch_config(overwrite=True) -> BatchConfig:
    return BatchConfig(
        shotgrid_project_id=123,
        overwrite=overwrite,
        shotgrid_url="http://google.com",
        script_name="1",
        script_key="1",
        fields_mapping={},
    )


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


def _avalon_collections(client: MongoClient) -> List[str]:
    return client.get_database(DbName.AVALON.value).list_collection_names()


def _intermediate_collections(client: MongoClient) -> List[str]:
    return client.get_database(
        DbName.INTERMEDIATE.value
    ).list_collection_names()


def _all_avalon(client: MongoClient) -> List[Map]:
    col = client.get_database(DbName.AVALON.value).list_collection_names()[0]
    return list(
        client.get_database(DbName.AVALON.value).get_collection(col).find({})
    )


def _all_intermediate(client: MongoClient) -> List[Map]:
    col = client.get_database(
        DbName.INTERMEDIATE.value
    ).list_collection_names()[0]
    return list(
        client.get_database(DbName.INTERMEDIATE.value)
        .get_collection(col)
        .find({})
    )


def _populate_db(db: Collection, data: List[Map]) -> None:
    db.delete_many({})
    db.insert_many(data)


@pytest.mark.asyncio
async def test_update_shotgrid_to_avalon_empty(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    data: List[Any] = []

    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(conn, "get_db_client", _fun(client))

    # Act
    await batch_controller.batch("1", _batch_config())

    # Assert
    assert_that(client.list_database_names()).is_length(0)


@pytest.mark.asyncio
async def test_update_shotgrid_to_avalon_init_project(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    client = MongoClient()
    project = _get_project()
    data = [project]

    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(conn, "get_db_client", _fun(client))

    # Act
    await batch_controller.batch(project["_id"], _batch_config())

    # Assert
    assert_that(client.list_database_names()).is_equal_to(
        [DbName.INTERMEDIATE.value, DbName.AVALON.value]
    )
    assert_that(_avalon_collections(client)).is_equal_to([project["_id"]])
    assert_that(_intermediate_collections(client)).is_equal_to(
        [project["_id"]]
    )


@pytest.mark.asyncio
async def test_update_shotgrid_to_avalon_update_project(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    client = MongoClient()
    project = _get_project()
    data = [project]

    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(conn, "get_db_client", _fun(client))

    project_avalon_init_data = _create_avalon_project_row(project["_id"])
    client.get_database(DbName.AVALON.value).get_collection(
        project["_id"]
    ).insert_one(project_avalon_init_data)
    # Act
    await batch_controller.batch(project["_id"], _batch_config(False))

    # Assert
    assert_that(_all_avalon(client)).is_length(1)
    assert_that(_all_avalon(client)).extracting(
        "type", filter={"type": "project"}
    ).is_equal_to(["project"])
    assert_that(_all_avalon(client)).extracting(
        "config", filter={"type": "project"}
    ).extract_keys().is_equal_to(
        {"apps", "imageio", "roots", "tasks", "templates"}
    )
    assert_that(_all_avalon(client)).extracting(
        "config", filter={"type": "project"}
    ).extracting("apps", "imageio", "roots", "templates").is_equal_to(
        [tuple([v for k, v in project_avalon_init_data["config"].items()])]
    )


@pytest.mark.asyncio
async def test_update_shotgrid_to_avalon_update_project_tasks(
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

    project_avalon_init_data = _create_avalon_project_row(project["_id"])
    client.get_database(DbName.AVALON.value).get_collection(
        project["_id"]
    ).insert_one(project_avalon_init_data)
    # Act
    await batch_controller.batch(project["_id"], _batch_config())

    # Assert
    assert_that(_all_avalon(client)).extracting(
        "config", filter={"type": "project"}
    ).extracting("tasks").is_length(1)
    assert_that(_all_avalon(client)).extracting(
        "config", filter={"type": "project"}
    ).extracting("tasks").extract_keys().contains(
        *[x["task_type"] for x in asset_and_type[2:]]
    )


@pytest.mark.asyncio
async def test_update_shotgrid_to_avalon_init_asset(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    project = _get_project()
    asset_grp = _get_asset_group(project)
    asset_and_type = _get_prp_asset(asset_grp)
    data = [project, asset_grp, *asset_and_type]

    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(conn, "get_db_client", _fun(client))

    # Act
    await batch_controller.batch(project["_id"], _batch_config())

    # Assert
    assert_that(_all_avalon(client)).extracting("type").is_equal_to(
        ["project"] + ["asset" for _ in range(3)]
    )
    assert_that(_all_intermediate(client)).is_length(len(data))
    assert_that(_all_intermediate(client)).except_by_key(
        "object_id"
    ).is_equal_to(data)


@pytest.mark.asyncio
async def test_update_shotgrid_to_avalon_overwrite(monkeypatch: MonkeyPatch):
    # Arrange
    project_id = "Project_bebc4f75"
    client = MongoClient()
    _populate_db(
        client.get_database(DbName.AVALON.value).get_collection(
            overwrite_data.OVERWRITE_PROJECT_ID
        ),
        overwrite_data.OVERWRITE_AVALON_DATA,
    )
    _populate_db(
        client.get_database(DbName.INTERMEDIATE.value).get_collection(
            overwrite_data.OVERWRITE_PROJECT_ID
        ),
        overwrite_data.OVERWRITE_INTERMEDIATE_DB_DATA,
    )
    monkeypatch.setattr(
        repository,
        "get_hierarchy_by_project",
        Mock(return_value=overwrite_data.OVERWRITE_SHOTGRID_DATA),
    )
    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    # Act
    await batch_controller.batch(project_id, _batch_config())

    # Assert
    assert_that(_avalon_collections(client)).is_length(1)
    assert_that(_all_avalon(client)).is_length(1)
    assert_that(_all_avalon(client)[0]["type"]).is_equal_to("project")
    assert_that(_all_avalon(client)[0]["name"]).is_equal_to(
        overwrite_data.OVERWRITE_INTERMEDIATE_DB_DATA[0]["_id"]
    )


@pytest.mark.asyncio
async def test_update_shotgrid_to_avalon_update_values(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    object_ids = list(range(2))
    client = MongoClient()
    project_id = update_values_data.PROJECT_ID
    _populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        update_values_data.AVALON_DATA,
    )
    _populate_db(
        client.get_database(DbName.INTERMEDIATE.value).get_collection(
            project_id
        ),
        update_values_data.INTERMEDIATE_DB_DATA,
    )
    monkeypatch.setattr(
        repository,
        "get_hierarchy_by_project",
        Mock(return_value=update_values_data.SHOTGRID_DATA),
    )
    monkeypatch.setattr(generator, "object_id", Mock(side_effect=object_ids))
    monkeypatch.setattr(conn, "get_db_client", _fun(client))

    # Act
    await batch_controller.batch(project_id, _batch_config())

    # Assert
    assert_that(_all_avalon(client)).is_length(
        len(update_values_data.AVALON_DATA)
    )
    assert_that(_all_avalon(client)).extracting("_id", "name").is_equal_to(
        [
            (
                x["_id"] if not x["name"] == "Fork" else object_ids[0],
                x["name"].replace("Fork", "Knife"),
            )
            for x in update_values_data.AVALON_DATA
        ]
    )
    assert_that(_all_avalon(client)).extracting(
        "_id", filter={"name": "Fork"}
    ).is_empty()


@pytest.mark.asyncio
async def test_update_shotgrid_to_avalon_update_asset_type(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    client = MongoClient()
    project_id = update_asset_data.PROJECT_ID
    _populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        update_asset_data.AVALON_DATA,
    )
    _populate_db(
        client.get_database(DbName.INTERMEDIATE.value).get_collection(
            project_id
        ),
        update_asset_data.INTERMEDIATE_DB_DATA,
    )
    object_ids = list(range(2))
    monkeypatch.setattr(
        repository,
        "get_hierarchy_by_project",
        Mock(return_value=update_asset_data.SHOTGRID_DATA),
    )
    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    monkeypatch.setattr(generator, "object_id", Mock(side_effect=object_ids))

    # Act
    await batch_controller.batch(project_id, _batch_config(False))

    # Assert
    assert_that(_all_avalon(client)).is_length(
        len(update_asset_data.AVALON_DATA) + 1
    )
    assert_that(_all_avalon(client)).extracting(
        "_id", filter={"name": "Fork"}
    ).is_in(object_ids[1:])
    assert_that(_all_avalon(client)).extracting(
        "_id", filter={"name": "PROPS"}
    ).is_in(object_ids[0:1])
    assert_that(_all_avalon(client)).extracting(
        "data", filter={"name": "Fork"}
    ).extracting("visualParent").is_equal_to(
        [_all_avalon(client)[-2:-1][0]["_id"]]
    )


@pytest.mark.asyncio
async def test_update_shotgrid_when_some_assets_deleted(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    client = MongoClient()
    project_id = delete_asset_data.PROJECT_ID
    _populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        delete_asset_data.AVALON_DATA,
    )
    _populate_db(
        client.get_database(DbName.INTERMEDIATE.value).get_collection(
            project_id
        ),
        delete_asset_data.INTERMEDIATE_DB_DATA,
    )
    monkeypatch.setattr(
        repository,
        "get_hierarchy_by_project",
        Mock(return_value=delete_asset_data.SHOTGRID_DATA),
    )
    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    # Act
    await batch_controller.batch(project_id, _batch_config(False))
    # Assert
    assert_that(_all_avalon(client)).is_length(
        len(delete_asset_data.AVALON_DATA) - 2
    )
