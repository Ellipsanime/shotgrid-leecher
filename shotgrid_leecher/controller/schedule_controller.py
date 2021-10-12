from shotgrid_leecher.controller.batch_controller import router
from shotgrid_leecher.domain import schedule_domain
from shotgrid_leecher.record.http_models import BatchConfig


@router.post("/{project_name}")
async def schedule_batch(project_name: str, batch_config: BatchConfig):
    command = batch_config.to_schedule_command(project_name)
    return schedule_domain.schedule_batch(command)
