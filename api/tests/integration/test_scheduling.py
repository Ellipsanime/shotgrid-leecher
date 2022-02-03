import uuid
from datetime import datetime
from typing import Dict, Any, List

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from mock import Mock
from mongomock.mongo_client import MongoClient

from controller import schedule_controller
from domain import batch_domain, schedule_domain
from record.commands import ScheduleShotgridBatchCommand
from record.enums import DbName, DbCollection
from record.results import BatchResult
from repository import avalon_repo
from utils import connectivity as conn
from utils.funcs import (
    batch_config,
    get_project,
    fun,
)

Map = Dict[str, Any]


def _all_projects(client: MongoClient) -> List[Map]:
    return list(
        client.get_database(DbName.SCHEDULE.value)
        .get_collection(DbCollection.SCHEDULE_PROJECTS.value)
        .find({})
    )


def _all_logs(client: MongoClient) -> List[Map]:
    return list(
        client.get_database(DbName.SCHEDULE.value)
        .get_collection(DbCollection.SCHEDULE_LOGS.value)
        .find({})
    )


def _rollin_projects(client: MongoClient, n=2):
    batches = [
        ScheduleShotgridBatchCommand.from_http_model(
            f"project_{str(uuid.uuid4())[:5]}", batch_config()
        )
        for _ in range(n)
    ]
    client.get_database(DbName.SCHEDULE.value).get_collection(
        DbCollection.SCHEDULE_PROJECTS.value
    ).insert_many(
        [{"_id": x.project_name, "command": x.to_dict()} for x in batches]
    )
    client.get_database(DbName.SCHEDULE.value).get_collection(
        DbCollection.SCHEDULE_QUEUE.value
    ).insert_many(
        [
            {
                "command": x.to_dict(),
                "datetime": datetime.utcnow(),
            }
            for x in batches
        ]
    )


@pytest.mark.asyncio
async def test_schedule_batch(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    project_name = f"project_{str(uuid.uuid4())[:5]}"
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    config = batch_config()
    # Act
    await schedule_controller.schedule_batch(project_name, config)

    # Assert
    assert_that(_all_projects(client)).extracting("_id").is_equal_to(
        [project_name]
    )
    assert_that(_all_projects(client)).extracting("command").extracting(
        "project_id"
    ).is_equal_to([config.shotgrid_project_id])
    assert_that(_all_projects(client)).extracting("command").extracting(
        "credentials"
    ).extracting("shotgrid_url").is_equal_to([config.shotgrid_url])


@pytest.mark.asyncio
async def test_dequeue_scheduled_batches(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    batch = Mock(return_value=BatchResult.OK)
    _rollin_projects(client, 3)
    project = get_project(f"project_{str(uuid.uuid4())[:5]}")
    monkeypatch.setattr(avalon_repo, "fetch_project", fun(project))
    monkeypatch.setattr(batch_domain, "update_shotgrid_in_avalon", batch)
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await schedule_domain.dequeue_and_process_batches()

    # Assert
    assert_that(_all_logs(client)).extracting("batch_result").is_equal_to(
        [BatchResult.OK.value, BatchResult.OK.value, BatchResult.OK.value]
    )


@pytest.mark.asyncio
async def test_dequeue_scheduled_batches_part_success(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    project = get_project(f"project_{str(uuid.uuid4())[:5]}")
    steps = []

    def _batch(_: Any):
        steps.append(1)
        if len(steps) == 1:
            return BatchResult.OK
        if len(steps) == 2:
            raise Exception("WAT!")
        if len(steps) == 3:
            return BatchResult.NO_SHOTGRID_HIERARCHY

    client = MongoClient()
    _rollin_projects(client, 3)
    monkeypatch.setattr(batch_domain, "update_shotgrid_in_avalon", _batch)
    monkeypatch.setattr(avalon_repo, "fetch_project", fun(project))
    monkeypatch.setattr(conn, "get_db_client", fun(client))
    # Act
    await schedule_domain.dequeue_and_process_batches()

    # Assert
    assert_that(_all_logs(client)).extracting("batch_result").is_equal_to(
        [
            BatchResult.OK.value,
            BatchResult.FAILURE.value,
            BatchResult.NO_SHOTGRID_HIERARCHY.value,
        ]
    )
