from dataclasses import asdict
from typing import Dict, Any

from fastapi import APIRouter

from shotgrid_leecher.domain import batch_domain
from shotgrid_leecher.record.commands import (
    ShotgridCheckCommand,
    ShotgridToAvalonBatchCommand,
)
from shotgrid_leecher.record.http_models import BatchConfig
from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials

router = APIRouter(tags=["batch"], prefix="/batch")


@router.post("/{project_name}")
async def batch(project_name: str, batch_config: BatchConfig):
    credentials = ShotgridCredentials(
        batch_config.shotgrid_url,
        batch_config.script_name,
        batch_config.script_key,
    )
    command = ShotgridToAvalonBatchCommand(
        batch_config.shotgrid_project_id,
        project_name,
        batch_config.overwrite,
        credentials,
    )
    return batch_domain.update_shotgrid_in_avalon(command)


@router.get("/{project_name}/check")
async def batch_check(
    project_name: str,
    shotgrid_url: str,
    shotgrid_project_id: int,
    script_name: str,
    script_key: str,
) -> Dict[str, Any]:
    cred = ShotgridCredentials(shotgrid_url, script_name, script_key)
    command = ShotgridCheckCommand(project_name, shotgrid_project_id, cred)
    return asdict(batch_domain.check_shotgrid_before_batch(command))
