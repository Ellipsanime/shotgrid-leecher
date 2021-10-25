from typing import List

from fastapi import APIRouter

from shotgrid_leecher.domain import schedule_domain
from shotgrid_leecher.record.commands import CancelBatchSchedulingCommand
from shotgrid_leecher.record.http_models import BatchConfig
from shotgrid_leecher.record.queries import FindEntityQuery
from shotgrid_leecher.record.schedule_structures import (
    ScheduleLog,
    ScheduleProject,
    ScheduleQueueItem,
)
from shotgrid_leecher.repository import schedule_repo

router = APIRouter(tags=["schedule"], prefix="/schedule")


@router.get("/projects")
async def projects() -> List[ScheduleProject]:
    return schedule_repo.fetch_scheduled_projects(FindEntityQuery())


@router.get("/queue")
async def queue() -> List[ScheduleQueueItem]:
    return schedule_repo.fetch_scheduled_queue(FindEntityQuery())


@router.get("/logs")
async def logs() -> List[ScheduleLog]:
    return schedule_repo.fetch_scheduled_logs(FindEntityQuery())


@router.post("/{project_name}")
async def schedule_batch(project_name: str, batch_config: BatchConfig):
    command = batch_config.to_schedule_command(project_name)
    return await schedule_domain.schedule_batch(command)


@router.delete("/{project_name}")
async def cancel_batch_scheduling(project_name: str):
    command = CancelBatchSchedulingCommand(project_name)
    return await schedule_domain.cancel_batch_scheduling(command)
