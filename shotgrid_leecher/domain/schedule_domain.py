from multiprocessing import Pool
from typing import Any

from starlette.concurrency import run_in_threadpool

import shotgrid_leecher.repository.schedule_repo as schedule_repo
from shotgrid_leecher.domain import batch_domain
from shotgrid_leecher.record.commands import (
    ScheduleShotgridBatchCommand,
    ShotgridToAvalonBatchCommand,
    LogBatchUpdateCommand,
)
from shotgrid_leecher.record.results import BatchResult
from shotgrid_leecher.utils.logger import get_logger
from shotgrid_leecher.writers import schedule_writer as writer, schedule_writer

_LOG = get_logger(__name__.split(".")[-1])

_UNROLL_BATCH_SIZE = 10


def schedule_batch(command: ScheduleShotgridBatchCommand) -> None:
    writer.request_scheduling(command)


async def queue_scheduled_batches() -> None:
    commands = schedule_repo.fetch_batch_commands()
    if not commands:
        return
    await run_in_threadpool(schedule_writer.queue_requests, commands)


async def dequeue_and_process_batches() -> None:
    with Pool() as pool:
        pool.map(_batch_and_log, range(_UNROLL_BATCH_SIZE))
    # for command in range(_UNROLL_BATCH_SIZE):
    #     await run_in_threadpool(_batch_and_log)


def _batch_and_log(_: Any) -> None:
    request = schedule_writer.dequeue_request()
    if not request:
        return None
    command = ShotgridToAvalonBatchCommand.from_dict(request.to_dict())
    try:
        result = batch_domain.update_shotgrid_in_avalon(command)
        log_command = LogBatchUpdateCommand(
            result,
            command.project_name,
            command.project_id,
            None,
        )
        schedule_writer.log_batch_result(log_command)
    except Exception as ex:
        log_command = LogBatchUpdateCommand(
            BatchResult.FAILURE,
            command.project_name,
            command.project_id,
            {"exception": ex.args[0]},
        )
        _LOG.error(ex)
        schedule_writer.log_batch_result(log_command)
