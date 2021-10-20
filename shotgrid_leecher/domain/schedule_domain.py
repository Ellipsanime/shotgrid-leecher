from typing import Any

from asyncio_pool import AioPool

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


async def schedule_batch(command: ScheduleShotgridBatchCommand) -> None:
    await writer.request_scheduling(command)


async def queue_scheduled_batches() -> Any:
    groups = await schedule_repo.group_batch_commands()
    already_queued = list({x.name for x in groups})
    commands = await schedule_repo.fetch_batch_commands(already_queued)
    if not commands:
        return

    return await schedule_writer.queue_requests(commands)


async def dequeue_and_process_batches() -> None:
    raw_count = await schedule_repo.count_projects()
    size = int(raw_count + raw_count * 0.15 + 1)
    pool = AioPool()
    await pool.map(_batch_and_log, range(size))


async def _batch_and_log(_: Any) -> None:
    request = await schedule_writer.dequeue_request()
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
        await schedule_writer.log_batch_result(log_command)
    except Exception as ex:
        log_command = LogBatchUpdateCommand(
            BatchResult.FAILURE,
            command.project_name,
            command.project_id,
            {"exception": ex.args[0]},
        )
        _LOG.error(ex)
        await schedule_writer.log_batch_result(log_command)
