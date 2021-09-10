from typing import Dict, Any, Optional

from fastapi import APIRouter
from pydantic import BaseModel
from pydantic.fields import Field

router = APIRouter(tags=["batch"], prefix="/batch")


class BatchConfig(BaseModel):
    shotgrid_url: str = Field(None, title="Shotgrid server url")
    shotgrid_project_id: int = Field(None, title="Shotgrid project id")
    script_name: str = Field(None, title="Shotgrid script name")
    script_key: str = Field(None, title="Shotgrid script key")
    fields_mapping: Optional[Dict[str, Any]]


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
