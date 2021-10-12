from starlette.concurrency import run_in_threadpool

import shotgrid_leecher.repository.schedule_repo as schedule_repo
from shotgrid_leecher.domain import batch_domain
from shotgrid_leecher.record.commands import (
    ScheduleShotgridBatchCommand,
    ShotgridToAvalonBatchCommand,
)
from shotgrid_leecher.repository import avalon_repo
from shotgrid_leecher.utils.logger import get_logger
from shotgrid_leecher.writers import schedule_writer as writer

_LOG = get_logger(__name__.split(".")[-1])


def schedule_batch(command: ScheduleShotgridBatchCommand) -> None:
    writer.request_scheduling(command)


async def unroll_batches() -> None:
    for command in schedule_repo.fetch_batch_commands():
        try:
            if not avalon_repo.get_project_entity(command.project_name):
                await run_in_threadpool(_create_and_log, command)
                continue
            await run_in_threadpool(_update_and_log, command)
        except Exception as ex:
            _LOG.error(ex)


def _create_and_log(command: ShotgridToAvalonBatchCommand) -> None:
    batch_domain.create_shotgrid_in_avalon(command)


def _update_and_log(command: ShotgridToAvalonBatchCommand) -> None:
    batch_domain.update_shotgrid_in_avalon(command)
