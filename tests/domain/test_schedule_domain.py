import random
import uuid
from typing import Any, Callable

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from mock import Mock

import shotgrid_leecher.repository.schedule_repo as schedule_repo
from shotgrid_leecher.domain import batch_domain, schedule_domain
from shotgrid_leecher.record.avalon_structures import (
    AvalonProject,
    AvalonProjectData,
)
from shotgrid_leecher.record.commands import ScheduleShotgridBatchCommand
from shotgrid_leecher.record.results import BatchResult, GroupAndCountResult
from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials
from shotgrid_leecher.record.shotgrid_subtypes import FieldsMapping
from shotgrid_leecher.repository import avalon_repo
from shotgrid_leecher.writers import schedule_writer


def _fun(param: Any) -> Callable[[Any], Any]:
    return lambda *_: param


async def _async_f(param: Any):
    return lambda *_: param


def _get_schedule_command() -> ScheduleShotgridBatchCommand:
    return ScheduleShotgridBatchCommand(
        random.randint(10 ** 2, 10 ** 5),
        str(uuid.uuid4()),
        ShotgridCredentials(
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            str(uuid.uuid4()),
        ),
        FieldsMapping.from_dict({}),
    )


def _get_group_result() -> GroupAndCountResult:
    return GroupAndCountResult(
        str(uuid.uuid4()),
        random.randint(10 ** 2, 10 ** 5),
    )


@pytest.mark.asyncio
async def test_queue_scheduled_when_no_commands(monkeypatch: MonkeyPatch):
    # Arrange
    group, fetch, queue = Mock(), Mock(), Mock()
    group.return_value = [_get_group_result(), _get_group_result()]
    fetch.return_value = []
    monkeypatch.setattr(schedule_repo, "group_batch_commands", group)
    monkeypatch.setattr(schedule_repo, "fetch_batch_commands", fetch)
    monkeypatch.setattr(schedule_writer, "queue_requests", queue)
    # Act
    await schedule_domain.queue_scheduled_batches()
    # Assert
    assert_that(queue.call_count).is_equal_to(0)


@pytest.mark.asyncio
async def test_queue_scheduled_working(monkeypatch: MonkeyPatch):
    # Arrange
    group, fetch, queue = Mock(), Mock(), Mock()
    group.return_value = [_get_group_result(), _get_group_result()]
    fetch.return_value = [_get_schedule_command()]
    monkeypatch.setattr(schedule_repo, "group_batch_commands", group)
    monkeypatch.setattr(schedule_repo, "fetch_batch_commands", fetch)
    monkeypatch.setattr(schedule_writer, "queue_requests", queue)
    # Act
    await schedule_domain.queue_scheduled_batches()
    # Assert
    assert_that(queue.call_count).is_equal_to(1)
    queue.assert_called_with(fetch.return_value)


@pytest.mark.asyncio
async def test_dequeue_and_process_when_success(monkeypatch: MonkeyPatch):
    # Arrange
    project = AvalonProject("", "", AvalonProjectData(), dict())
    count, batch, dequeue, proj, log = (
        Mock(return_value=1),
        Mock(return_value=BatchResult.OK),
        Mock(return_value=_get_schedule_command()),
        Mock(return_value=project),
        Mock(),
    )
    monkeypatch.setattr(avalon_repo, "fetch_project", proj)
    monkeypatch.setattr(schedule_repo, "count_projects", count)
    monkeypatch.setattr(batch_domain, "update_shotgrid_in_avalon", batch)
    monkeypatch.setattr(schedule_writer, "dequeue_request", dequeue)
    monkeypatch.setattr(schedule_writer, "log_batch_result", log)
    # Act
    await schedule_domain.dequeue_and_process_batches()

    # Assert
    assert_that(batch.call_count).is_equal_to(2)
    assert_that(log.call_count).is_equal_to(2)
    assert_that(log.call_args_list[0][0][0].batch_result).is_equal_to(
        BatchResult.OK
    )
    assert_that(log.call_args_list[1][0][0].batch_result).is_equal_to(
        BatchResult.OK
    )


@pytest.mark.asyncio
async def test_dequeue_and_process_when_no_hierarchy(monkeypatch: MonkeyPatch):
    # Arrange
    project = AvalonProject("", "", AvalonProjectData(), dict())
    count, batch, dequeue, proj, log = (
        Mock(return_value=0),
        Mock(return_value=BatchResult.NO_SHOTGRID_HIERARCHY),
        Mock(return_value=_get_schedule_command()),
        Mock(return_value=project),
        Mock(),
    )

    monkeypatch.setattr(avalon_repo, "fetch_project", proj)
    monkeypatch.setattr(schedule_repo, "count_projects", count)
    monkeypatch.setattr(batch_domain, "update_shotgrid_in_avalon", batch)
    monkeypatch.setattr(schedule_writer, "dequeue_request", dequeue)
    monkeypatch.setattr(schedule_writer, "log_batch_result", log)
    # Act
    await schedule_domain.dequeue_and_process_batches()

    # Assert
    assert_that(batch.call_count).is_equal_to(1)
    assert_that(log.call_count).is_equal_to(1)
    assert_that(log.call_args_list[0][0][0].batch_result).is_equal_to(
        BatchResult.NO_SHOTGRID_HIERARCHY
    )


@pytest.mark.asyncio
async def test_dequeue_and_process_when_failure(monkeypatch: MonkeyPatch):
    # Arrange
    project = AvalonProject("", "", AvalonProjectData(), dict())
    proj = Mock(return_value=project)
    count, log, dequeue = Mock(), Mock(), Mock()
    count.return_value = 0
    dequeue.return_value = _get_schedule_command()
    ex = "Oh no"

    def batch(_):
        raise Exception(ex)

    monkeypatch.setattr(avalon_repo, "fetch_project", proj)
    monkeypatch.setattr(batch_domain, "update_shotgrid_in_avalon", batch)
    monkeypatch.setattr(schedule_repo, "count_projects", count)
    monkeypatch.setattr(schedule_writer, "dequeue_request", dequeue)
    monkeypatch.setattr(schedule_writer, "log_batch_result", log)
    # Act
    await schedule_domain.dequeue_and_process_batches()
    # Assert
    assert_that(log.call_count).is_equal_to(1)
    assert_that(log.call_args_list[0][0][0].batch_result).is_equal_to(
        BatchResult.FAILURE
    )
    assert_that(log.call_args_list[0][0][0].data["exception"]).is_equal_to(ex)
