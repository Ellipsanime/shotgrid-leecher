from typing import Dict, Any

from fastapi import APIRouter

from shotgrid_leecher.record.http_models import BatchConfig

router = APIRouter(tags=["batch"], prefix="/batch")


@router.post("/{project_name}")
async def batch(project_name: str, batch_config: BatchConfig):
    return "Done"


@router.get("/{project_name}/check")
async def batch_status(
    project_name: str,
    shotgrid_url: str,
    shotgrid_project_id: int,
    script_name: str,
    script_key: str,
) -> Dict[str, Any]:
    return {"status": "OK"}
