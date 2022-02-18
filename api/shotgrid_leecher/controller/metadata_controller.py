from typing import Dict, Any

from fastapi import APIRouter

from shotgrid_leecher.const import PROJECT_META

router = APIRouter(tags=["meta"], prefix="/meta")


@router.get("")
async def version() -> Dict[str, Any]:
    return PROJECT_META
