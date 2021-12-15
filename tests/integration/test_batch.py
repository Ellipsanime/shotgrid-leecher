import random
import uuid
from typing import Any, Dict, List
from unittest.mock import Mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from fastapi import HTTPException
from mongomock import MongoClient, ObjectId

import shotgrid_leecher.repository.shotgrid_hierarchy_repo as repository
import shotgrid_leecher.utils.connectivity as conn
from asset import (
    overwrite_data,
    update_values_data,
    update_asset_data,
    delete_asset_data,
)
from shotgrid_leecher.controller import batch_controller
from shotgrid_leecher.mapper import intermediate_mapper
from shotgrid_leecher.record.avalon_structures import (
    AvalonProject,
    AvalonProjectData,
)
from shotgrid_leecher.record.enums import DbName, ShotgridType
from shotgrid_leecher.repository import avalon_repo
from shotgrid_leecher.utils import generator
from utils.funcs import (
    batch_config,
    avalon_collections,
    all_avalon,
    fun,
    intermediate_collections,
    all_intermediate,
    populate_db,
    params,
)

TASK_NAMES = ["lines", "color", "look", "dev"]
STEP_NAMES = ["modeling", "shading", "rigging"]

Map = Dict[str, Any]


def _generate_shotgrid_id() -> int:
    return uuid.uuid4().int & (1 << 16) - 1


def _get_project(project_id=f"Project_{str(uuid.uuid4())[0:8]}"):
    return intermediate_mapper.to_row(
        {
            "_id": project_id,
            "src_id": 111,
            "type": ShotgridType.PROJECT.value,
            "code": "code1",
            "parent": None,
            "params": params().to_dict(),
            "config": {
                "steps": [{"code": x, "short_name": x[:1]} for x in STEP_NAMES]
            },
        }
    )


def _get_asset_group(project_id: str):

    return intermediate_mapper.to_row(
        {
            "_id": ShotgridType.ASSET.value,
            "type": ShotgridType.GROUP.value,
            "parent": f",{project_id},",
            "params": params().to_dict(),
        }
    )


def _get_shot_group(project):

    return intermediate_mapper.to_row(
        {
            "_id": ShotgridType.SHOT.value,
            "type": ShotgridType.GROUP.value,
            "parent": f",{project['_id']},",
            "params": params().to_dict(),
        }
    )


def _get_prp_asset(parent):

    return [
        intermediate_mapper.to_row(x)
        for x in [
            {
                "_id": "PRP",
                "type": ShotgridType.GROUP.value,
                "parent": f"{parent.parent}{parent.id},",
                "params": params().to_dict(),
            },
            {
                "_id": "Fork",
                "src_id": _generate_shotgrid_id(),
                "type": ShotgridType.ASSET.value,
                "parent": f"{parent.parent}{parent.id},PRP,",
                "params": params().to_dict(),
            },
        ]
    ]


def _get_prp_asset_with_tasks(parent, task_num):
    asset = _get_prp_asset(parent)
    tasks = [
        intermediate_mapper.to_row(
            {
                "_id": f"{random.choice(TASK_NAMES)}_{uuid.uuid4().int}",
                "src_id": _generate_shotgrid_id(),
                "type": ShotgridType.TASK.value,
                "task_type": random.choice(STEP_NAMES),
                "params": params().to_dict(),
                "parent": f"{asset[1].parent}{asset[1].id},",
            }
        )
        for _ in range(task_num)
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
            "tasks": {x: {"short_name": x[:1]} for x in STEP_NAMES},
        },
        "data": {},
    }


@pytest.mark.asyncio
async def test_update_shotgrid_to_avalon_empty(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    data: List[Any] = []
    project = AvalonProject("", "", AvalonProjectData(), dict())
    monkeypatch.setattr(avalon_repo, "fetch_project", fun(project))
    monkeypatch.setattr(repository, "get_hierarchy_by_project", fun(data))
    monkeypatch.setattr(conn, "get_db_client", fun(client))

    # Act
    await batch_controller.batch_update("1", batch_config())

    # Assert
    assert_that(client.list_database_names()).is_length(0)


@pytest.mark.asyncio
async def test_update_shotgrid_to_avalon_init_project(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    client = MongoClient()
    data = [_get_project()]
    project = AvalonProject(
        str(ObjectId()),
        data[0].id,
        AvalonProjectData(),
        dict(),
    )
    monkeypatch.setattr(avalon_repo, "fetch_project", fun(project))
    monkeypatch.setattr(repository, "get_hierarchy_by_project", fun(data))
    monkeypatch.setattr(conn, "get_db_client", fun(client))

    # Act
    await batch_controller.batch_update(data[0].id, batch_config())

    # Assert
    assert_that(client.list_database_names()).is_equal_to(
        [DbName.INTERMEDIATE.value, DbName.AVALON.value]
    )
    assert_that(avalon_collections(client)).is_equal_to([data[0].id])
    assert_that(intermediate_collections(client)).is_equal_to([data[0].id])


@pytest.mark.asyncio
async def test_update_shotgrid_to_avalon_update_project(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    client = MongoClient()
    project = _get_project()
    data = [project]

    monkeypatch.setattr(repository, "get_hierarchy_by_project", fun(data))
    monkeypatch.setattr(conn, "get_db_client", fun(client))

    project_avalon_init_data = _create_avalon_project_row(project.id)
    client.get_database(DbName.AVALON.value).get_collection(
        project.id
    ).insert_one(project_avalon_init_data)
    # Act
    await batch_controller.batch_update(project.id, batch_config(False))

    # Assert
    assert_that(all_avalon(client)).is_length(1)
    assert_that(all_avalon(client)).extracting(
        "type", filter={"type": "project"}
    ).is_equal_to(["project"])
    assert_that(all_avalon(client)).extracting(
        "config", filter={"type": "project"}
    ).extract_keys().is_equal_to(
        {"apps", "imageio", "roots", "tasks", "templates"}
    )
    assert_that(all_avalon(client)).extracting(
        "config", filter={"type": "project"}
    ).extracting("apps", "imageio", "roots", "templates").is_equal_to(
        [
            tuple(
                [
                    v
                    for k, v in project_avalon_init_data["config"].items()
                    if k != "tasks"
                ]
            )
        ]
    )


@pytest.mark.asyncio
async def test_update_batch_when_projects_with_different_source_name(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    client = MongoClient()
    data = [_get_project()]
    project = AvalonProject(
        str(ObjectId()),
        data[0].id,
        AvalonProjectData(),
        dict(),
    )
    monkeypatch.setattr(avalon_repo, "fetch_project", fun(project))
    monkeypatch.setattr(repository, "get_hierarchy_by_project", fun(data))
    monkeypatch.setattr(conn, "get_db_client", fun(client))

    project_avalon_init_data = _create_avalon_project_row(data[0].id)
    client.get_database(DbName.AVALON.value).get_collection(
        data[0].id
    ).insert_one(project_avalon_init_data)

    with pytest.raises(HTTPException) as ex:
        # Act
        await batch_controller.batch_update(
            "fictitious_project_name",
            batch_config(False),
        )
        # Assert
        assert_that(ex.status_code).is_equal_to(500)
        assert_that(all_avalon(client)).is_length(1)


@pytest.mark.asyncio
async def test_update_shotgrid_to_avalon_update_project_tasks(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    task_num = 3
    client = MongoClient()
    project = _get_project()
    asset_grp = _get_asset_group(project.id)
    asset_and_type = _get_prp_asset_with_tasks(asset_grp, task_num)
    data = [project, asset_grp, *asset_and_type]

    monkeypatch.setattr(repository, "get_hierarchy_by_project", fun(data))
    monkeypatch.setattr(conn, "get_db_client", fun(client))

    project_avalon_init_data = _create_avalon_project_row(project.id)
    client.get_database(DbName.AVALON.value).get_collection(
        project.id
    ).insert_one(project_avalon_init_data)
    # Act
    await batch_controller.batch_update(project.id, batch_config())

    # Assert
    assert_that(all_avalon(client)).extracting(
        "config", filter={"type": "project"}
    ).extracting("tasks").is_length(1)
    assert_that(all_avalon(client)).extracting(
        "config", filter={"type": "project"}
    ).extracting("tasks").extract_keys().contains(
        *[x.task_type for x in asset_and_type[2:]]
    )


@pytest.mark.asyncio
async def test_update_shotgrid_to_avalon_init_asset(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    project_id = str(uuid.uuid4())[0:8]
    asset_grp = _get_asset_group(project_id)
    asset_and_type = _get_prp_asset(asset_grp)
    data = [_get_project(project_id), asset_grp, *asset_and_type]
    project = AvalonProject(
        str(ObjectId()),
        project_id,
        AvalonProjectData(),
        dict(),
    )
    monkeypatch.setattr(avalon_repo, "fetch_project", fun(project))
    monkeypatch.setattr(repository, "get_hierarchy_by_project", fun(data))
    monkeypatch.setattr(conn, "get_db_client", fun(client))

    # Act
    await batch_controller.batch_update(project_id, batch_config())

    # Assert
    assert_that(all_avalon(client)).extracting("type").is_equal_to(
        ["project"] + ["asset" for _ in range(3)]
    )
    assert_that(all_intermediate(client)).is_length(len(data))
    assert_that(all_intermediate(client)).except_by_key(
        "object_id"
    ).extracting("_id").is_equal_to([x.id for x in data])


@pytest.mark.asyncio
async def test_update_shotgrid_to_avalon_overwrite(monkeypatch: MonkeyPatch):
    # Arrange
    project_id = "Project_bebc4f75"
    client = MongoClient()
    populate_db(
        client.get_database(DbName.AVALON.value).get_collection(
            overwrite_data.OVERWRITE_PROJECT_ID
        ),
        overwrite_data.OVERWRITE_AVALON_DATA,
    )
    populate_db(
        client.get_database(DbName.INTERMEDIATE.value).get_collection(
            overwrite_data.OVERWRITE_PROJECT_ID
        ),
        overwrite_data.OVERWRITE_INTERMEDIATE_DB_DATA,
    )
    monkeypatch.setattr(
        repository,
        "get_hierarchy_by_project",
        Mock(
            return_value=[
                intermediate_mapper.to_row(x)
                for x in overwrite_data.OVERWRITE_SHOTGRID_DATA
            ]
        ),
    )
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await batch_controller.batch_update(project_id, batch_config())

    # Assert
    assert_that(avalon_collections(client)).is_length(1)
    assert_that(all_avalon(client)).is_length(1)
    assert_that(all_avalon(client)[0]["type"]).is_equal_to("project")
    assert_that(all_avalon(client)[0]["name"]).is_equal_to(
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
    populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        update_values_data.AVALON_DATA,
    )
    populate_db(
        client.get_database(DbName.INTERMEDIATE.value).get_collection(
            project_id
        ),
        update_values_data.INTERMEDIATE_DB_DATA,
    )
    monkeypatch.setattr(
        repository,
        "get_hierarchy_by_project",
        Mock(
            return_value=[
                intermediate_mapper.to_row(x)
                for x in update_values_data.SHOTGRID_DATA
            ]
        ),
    )
    monkeypatch.setattr(generator, "object_id", Mock(side_effect=object_ids))
    monkeypatch.setattr(conn, "get_db_client", fun(client))

    # Act
    await batch_controller.batch_update(project_id, batch_config())

    # Assert
    assert_that(all_avalon(client)).is_length(
        len(update_values_data.AVALON_DATA)
    )
    assert_that(all_avalon(client)).extracting("_id", "name").is_equal_to(
        [
            (
                x["_id"] if not x["name"] == "Fork" else object_ids[0],
                x["name"].replace("Fork", "Knife"),
            )
            for x in update_values_data.AVALON_DATA
        ]
    )
    assert_that(all_avalon(client)).extracting(
        "_id", filter={"name": "Fork"}
    ).is_empty()


@pytest.mark.asyncio
async def test_update_shotgrid_to_avalon_update_asset_type(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    client = MongoClient()
    project_id = update_asset_data.PROJECT_ID
    populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        update_asset_data.AVALON_DATA,
    )
    populate_db(
        client.get_database(DbName.INTERMEDIATE.value).get_collection(
            project_id
        ),
        update_asset_data.INTERMEDIATE_DB_DATA,
    )
    object_ids = list(range(2))
    monkeypatch.setattr(
        repository,
        "get_hierarchy_by_project",
        Mock(
            return_value=[
                intermediate_mapper.to_row(x)
                for x in update_asset_data.SHOTGRID_DATA
            ]
        ),
    )
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    monkeypatch.setattr(generator, "object_id", Mock(side_effect=object_ids))

    # Act
    await batch_controller.batch_update(project_id, batch_config(False))

    # Assert
    assert_that(all_avalon(client)).is_length(
        len(update_asset_data.AVALON_DATA) + 1
    )
    assert_that(all_avalon(client)).extracting(
        "_id", filter={"name": "Fork"}
    ).is_in(object_ids[1:])
    assert_that(all_avalon(client)).extracting(
        "_id", filter={"name": "PROPS"}
    ).is_in(object_ids[0:1])
    assert_that(all_avalon(client)).extracting(
        "data", filter={"name": "Fork"}
    ).extracting("visualParent").is_equal_to(
        [all_avalon(client)[-2:-1][0]["_id"]]
    )


@pytest.mark.asyncio
async def test_update_shotgrid_when_some_assets_deleted(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    client = MongoClient()
    project_id = delete_asset_data.PROJECT_ID
    populate_db(
        client.get_database(DbName.AVALON.value).get_collection(project_id),
        delete_asset_data.AVALON_DATA,
    )
    populate_db(
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
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await batch_controller.batch_update(project_id, batch_config(False))
    # Assert
    assert_that(all_avalon(client)).is_length(
        len(delete_asset_data.AVALON_DATA) - 2
    )
