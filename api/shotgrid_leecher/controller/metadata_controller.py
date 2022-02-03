from typing import Dict, Any

from fastapi import APIRouter

from const import PROJECT_META

router = APIRouter(tags=["meta"], prefix="/meta")


@router.get("")
async def version() -> Dict[str, Any]:
    return PROJECT_META
