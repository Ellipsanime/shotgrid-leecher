import random
import uuid
from typing import Any, Callable
from unittest.mock import Mock

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that

import shotgrid_leecher.repository.schedule_repo as schedule_repo
from shotgrid_leecher.domain import batch_domain, schedule_domain
from shotgrid_leecher.record.commands import ScheduleShotgridBatchCommand
from shotgrid_leecher.record.results import BatchResult
from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials
from shotgrid_leecher.record.shotgrid_subtypes import FieldsMapping
from shotgrid_leecher.writers import schedule_writer


def _fun(param: Any) -> Callable[[Any], Any]:
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


@pytest.mark.asyncio
async def test_unroll_batches_when_success(monkeypatch: MonkeyPatch):
    # Arrange
    batch_commands = [_get_schedule_command(), _get_schedule_command()]
    batch, fetch, log = Mock(), Mock(), Mock()
    fetch.return_value = batch_commands
    batch.return_value = BatchResult.OK
    log.return_value = None
    monkeypatch.setattr(batch_domain, "update_shotgrid_in_avalon", batch)
    monkeypatch.setattr(schedule_repo, "fetch_batch_commands", fetch)
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
async def test_unroll_batches_when_no_hierarchy(monkeypatch: MonkeyPatch):
    # Arrange
    batch_commands = [_get_schedule_command(), _get_schedule_command()]
    batch, fetch, log = Mock(), Mock(), Mock()
    fetch.return_value = batch_commands
    batch.side_effect = [BatchResult.OK, BatchResult.NO_SHOTGRID_HIERARCHY]
    log.return_value = None
    monkeypatch.setattr(batch_domain, "update_shotgrid_in_avalon", batch)
    monkeypatch.setattr(schedule_repo, "fetch_batch_commands", fetch)
    monkeypatch.setattr(schedule_writer, "log_batch_result", log)
    # Act
    await schedule_domain.dequeue_and_process_batches()
    # Assert
    assert_that(batch.call_count).is_equal_to(2)
    assert_that(log.call_count).is_equal_to(2)
    assert_that(log.call_args_list[1][0][0].batch_result).is_equal_to(
        BatchResult.NO_SHOTGRID_HIERARCHY
    )


@pytest.mark.asyncio
async def test_unroll_batches_when_failure(monkeypatch: MonkeyPatch):
    # Arrange
    batch_commands = [_get_schedule_command(), _get_schedule_command()]
    fetch, log = Mock(), Mock()
    fetch.return_value = batch_commands
    ex = "Oh no"

    def batch(_):
        raise Exception(ex)

    log.return_value = None
    monkeypatch.setattr(batch_domain, "update_shotgrid_in_avalon", batch)
    monkeypatch.setattr(schedule_repo, "fetch_batch_commands", fetch)
    monkeypatch.setattr(schedule_writer, "log_batch_result", log)
    # Act
    await schedule_domain.dequeue_and_process_batches()
    # Assert
    assert_that(log.call_count).is_equal_to(2)
    assert_that(log.call_args_list[0][0][0].batch_result).is_equal_to(
        BatchResult.FAILURE
    )
    assert_that(log.call_args_list[1][0][0].batch_result).is_equal_to(
        BatchResult.FAILURE
    )
    assert_that(log.call_args_list[0][0][0].data["exception"]).is_equal_to(ex)
    assert_that(log.call_args_list[1][0][0].data["exception"]).is_equal_to(ex)
