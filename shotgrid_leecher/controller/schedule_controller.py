from fastapi import APIRouter

from shotgrid_leecher.domain import schedule_domain
from shotgrid_leecher.record.commands import CancelBatchSchedulingCommand
from shotgrid_leecher.record.http_models import BatchConfig

router = APIRouter(tags=["schedule"], prefix="/schedule")


@router.post("/{project_name}")
async def schedule_batch(project_name: str, batch_config: BatchConfig):
    command = batch_config.to_schedule_command(project_name)
    return await schedule_domain.schedule_batch(command)


@router.delete("/{project_name}")
async def cancel_batch_scheduling(project_name: str):
    command = CancelBatchSchedulingCommand(project_name)
    return await schedule_domain.cancel_batch_scheduling(command)
