from typing import Dict, Any

from attr import asdict
from fastapi import APIRouter, HTTPException

from shotgrid_leecher.domain import batch_domain
from shotgrid_leecher.record.commands import (
    ShotgridCheckCommand,
    UpdateShotgridInAvalonCommand,
    CreateShotgridInAvalonCommand,
)
from shotgrid_leecher.record.http_models import BatchConfig
from shotgrid_leecher.record.leecher_structures import ShotgridCredentials
from shotgrid_leecher.record.results import BatchResult
from shotgrid_leecher.repository import avalon_repo, config_repo

router = APIRouter(tags=["batch"], prefix="/batch")


def _get_credentials(batch_config: BatchConfig) -> ShotgridCredentials:
    credentials = config_repo.find_credentials_by_url(batch_config.shotgrid_url)
    if not credentials:
        raise HTTPException(
            status_code=404,
            detail="Credentials not found",
        )
    return credentials


@router.put("/{project_name}")
async def batch_create(project_name: str, batch_config: BatchConfig):
    command = CreateShotgridInAvalonCommand.from_http_model(
        project_name, _get_credentials(batch_config), batch_config
    )
    result = batch_domain.create_shotgrid_in_avalon(command)

    if result == BatchResult.WRONG_PROJECT_NAME:
        raise HTTPException(
            status_code=500,
            detail="Openpype and Shotgrid project name does not correspond",
        )
    return result


@router.post("/{project_name}")
async def batch_update(
    project_name: str,
    batch_config: BatchConfig,
):
    project = avalon_repo.fetch_project(project_name)
    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"No project found for {project_name}",
        )
    command = UpdateShotgridInAvalonCommand.from_http_model(
        project_name,
        _get_credentials(batch_config),
        batch_config,
        project.data,
    )
    result = batch_domain.update_shotgrid_in_avalon(command)

    if result == BatchResult.WRONG_PROJECT_NAME:
        raise HTTPException(
            status_code=500,
            detail="Openpype and Shotgrid project name does not correspond",
        )
    return result


@router.get("/check")
async def batch_check(
    shotgrid_url: str,
    shotgrid_project_id: int,
    script_name: str,
    script_key: str,
) -> Dict[str, Any]:
    cred = ShotgridCredentials(shotgrid_url, script_name, script_key)
    command = ShotgridCheckCommand(shotgrid_project_id, cred)
    return asdict(batch_domain.check_shotgrid_before_batch(command))
