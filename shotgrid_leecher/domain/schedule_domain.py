from starlette.concurrency import run_in_threadpool

import shotgrid_leecher.repository.schedule_repo as schedule_repo
from shotgrid_leecher.domain import batch_domain
from shotgrid_leecher.record.commands import (
    ScheduleShotgridBatchCommand,
    ShotgridToAvalonBatchCommand,
)
from shotgrid_leecher.utils.logger import get_logger
from shotgrid_leecher.writers import schedule_writer as writer

_LOG = get_logger(__name__.split(".")[-1])


def schedule_batch(command: ScheduleShotgridBatchCommand) -> None:
    writer.request_scheduling(command)


async def unroll_batches() -> None:
    for command in schedule_repo.fetch_batch_commands():
        await run_in_threadpool(_batch_and_log, command)


def _batch_and_log(schedule_command: ScheduleShotgridBatchCommand) -> None:
    try:
        command = ShotgridToAvalonBatchCommand.from_dict(
            schedule_command.to_dict()
        )
        batch_domain.update_shotgrid_in_avalon(command)
    except Exception as ex:
        _LOG.error(ex)
