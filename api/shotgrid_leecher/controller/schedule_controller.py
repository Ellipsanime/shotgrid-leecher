from typing import List

from fastapi import APIRouter, Depends

from domain import schedule_domain
from mapper import query_mapper
from record.commands import (
    CancelBatchSchedulingCommand,
    ScheduleShotgridBatchCommand,
)
from record.http_models import (
    BatchConfig,
    ScheduleQueryParams,
)
from record.schedule_structures import (
    ScheduleLog,
    ScheduleProject,
    ScheduleQueueItem,
)
from repository import schedule_repo

router = APIRouter(tags=["schedule"], prefix="/schedule")


@router.get("/projects")
async def projects(
    params: ScheduleQueryParams = Depends(ScheduleQueryParams),
) -> List[ScheduleProject]:
    query = query_mapper.http_to_find_query(params)
    return schedule_repo.fetch_scheduled_projects(query)


@router.get("/queue")
async def queue(
    params: ScheduleQueryParams = Depends(ScheduleQueryParams),
) -> List[ScheduleQueueItem]:
    query = query_mapper.http_to_find_query(params)
    return schedule_repo.fetch_scheduled_queue(query)


@router.get("/logs")
async def logs(
    params: ScheduleQueryParams = Depends(ScheduleQueryParams),
) -> List[ScheduleLog]:
    query = query_mapper.http_to_find_query(params)
    return schedule_repo.fetch_scheduled_logs(query)


@router.post("/{project_name}")
async def schedule_batch(project_name: str, batch_config: BatchConfig):
    command = ScheduleShotgridBatchCommand.from_http_model(
        project_name, batch_config
    )
    return await schedule_domain.schedule_batch(command)


@router.delete("/{project_name}")
async def cancel_batch_scheduling(project_name: str):
    command = CancelBatchSchedulingCommand(project_name)
    return await schedule_domain.cancel_batch_scheduling(command)
