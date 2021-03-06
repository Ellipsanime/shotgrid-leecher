from typing import List

from fastapi import APIRouter, Depends, HTTPException

from shotgrid_leecher.domain import schedule_domain
from shotgrid_leecher.mapper import query_mapper
from shotgrid_leecher.record.commands import (
    CancelBatchSchedulingCommand,
    ScheduleShotgridBatchCommand,
)
from shotgrid_leecher.record.http_models import (
    BatchConfig,
    ScheduleQueryParams,
)
from shotgrid_leecher.record.leecher_structures import (
    ScheduleLog,
    ScheduleProject,
    ScheduleQueueItem,
    EnhancedScheduleProject,
)
from shotgrid_leecher.record.queries import FindEntityQuery
from shotgrid_leecher.repository import schedule_repo, config_repo

router = APIRouter(tags=["schedule"], prefix="/schedule")


@router.get("/projects")
async def projects(
    params: ScheduleQueryParams = Depends(ScheduleQueryParams),
) -> List[ScheduleProject]:
    query = query_mapper.http_to_find_query(params)
    return schedule_repo.fetch_scheduled_projects(query)


@router.get("/enhanced-projects")
async def enhanced_projects(
    params: ScheduleQueryParams = Depends(ScheduleQueryParams),
) -> List[EnhancedScheduleProject]:
    query = query_mapper.http_to_find_query(params)
    return schedule_repo.fetch_enhanced_projects(query)


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
    credentials = config_repo.find_credentials_by_url(batch_config.shotgrid_url)
    if not credentials:
        raise HTTPException(
            status_code=404,
            detail="Credentials not found",
        )
    query = FindEntityQuery({"_id": project_name}, limit=1)
    if schedule_repo.fetch_scheduled_projects(query):
        raise HTTPException(
            status_code=422,
            detail=f"Project {project_name} already exists",
        )
    command = ScheduleShotgridBatchCommand.from_http_model(
        project_name, credentials, batch_config
    )
    return await schedule_domain.schedule_batch(command)


@router.delete("/{project_name}")
async def cancel_batch_scheduling(project_name: str):
    command = CancelBatchSchedulingCommand(project_name)
    return await schedule_domain.cancel_batch_scheduling(command)
