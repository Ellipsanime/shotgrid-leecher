import sys
import time
import traceback
from datetime import datetime
from typing import Any, Dict

from starlette.concurrency import run_in_threadpool

import shotgrid_leecher.repository.schedule_repo as schedule_repo
from shotgrid_leecher.domain import batch_domain
from shotgrid_leecher.record.commands import (
    ScheduleShotgridBatchCommand,
    UpdateShotgridInAvalonCommand,
    LogBatchUpdateCommand,
    CancelBatchSchedulingCommand,
    CleanScheduleBatchLogsCommand,
)
from shotgrid_leecher.record.results import BatchResult, ScheduleResult
from shotgrid_leecher.repository import avalon_repo
from shotgrid_leecher.utils.functional import try_or
from shotgrid_leecher.utils.logger import get_logger
from shotgrid_leecher.writers import schedule_writer as writer, schedule_writer

_LOG = get_logger(__name__.split(".")[-1])

_UNROLL_BATCH_SIZE = 10


async def schedule_clean_batch_log(
    command: CleanScheduleBatchLogsCommand,
) -> ScheduleResult:
    writer.clean_schedule_batch_logs(command)
    return ScheduleResult.OK


async def schedule_batch(command: ScheduleShotgridBatchCommand) -> BatchResult:
    writer.request_scheduling(command)
    return BatchResult.OK


async def queue_scheduled_batches() -> Dict[str, Any]:
    groups = schedule_repo.group_batch_commands()
    already_queued = list({x.name for x in groups})
    commands = schedule_repo.fetch_batch_commands(already_queued)
    if not commands:
        return dict()

    return schedule_writer.queue_requests(commands)


async def dequeue_and_process_batches() -> None:
    raw_count = schedule_repo.count_projects()
    size = int(raw_count + raw_count * 0.15 + 1)
    for x in range(size):
        await run_in_threadpool(_batch_and_log, x)


async def cancel_batch_scheduling(
    command: CancelBatchSchedulingCommand,
) -> Dict[str, Any]:
    return schedule_writer.remove_scheduled_project(command)


def _batch_and_log(_: Any) -> None:
    request = schedule_writer.dequeue_request()
    if not request:
        return None
    start = time.time()
    try:
        project_data = avalon_repo.fetch_project(request.project_name).data
        command = UpdateShotgridInAvalonCommand.from_dict(
            {**request.to_dict(), "project_data": project_data.to_dict()}
        )
        result = batch_domain.update_shotgrid_in_avalon(command)
        log_command = LogBatchUpdateCommand(
            result,
            command.project_name,
            command.project_id,
            time.time() - start,
            None,
            datetime.now(),
        )
        schedule_writer.log_batch_result(log_command)
    except Exception as ex:
        _, _, ex_traceback = sys.exc_info()
        traceback.print_tb(ex_traceback, limit=10, file=sys.stdout)
        log_command = LogBatchUpdateCommand(
            BatchResult.FAILURE,
            request.project_name,
            request.project_id,
            time.time() - start,
            {
                "exception": try_or(lambda x: x[0], ex.args, ex.args),
                "traceback": traceback.format_tb(ex_traceback, 100),
            },
            datetime.now(),
        )
        _LOG.error(ex)
        schedule_writer.log_batch_result(log_command)
