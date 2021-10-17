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


def schedule_batch(command: ScheduleShotgridBatchCommand) -> None:
    writer.request_scheduling(command)


async def rollin_batches() -> None:
    commands = schedule_repo.fetch_batch_commands()
    await run_in_threadpool(schedule_writer.queue_requests, commands)


async def unroll_batches() -> None:
    for command in schedule_repo.fetch_batch_commands():
        await run_in_threadpool(_batch_and_log, command)


def _batch_and_log(schedule_command: ScheduleShotgridBatchCommand) -> None:
    command = ShotgridToAvalonBatchCommand.from_dict(
        schedule_command.to_dict()
    )
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
