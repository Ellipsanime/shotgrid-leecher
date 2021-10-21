from fastapi import APIRouter

router = APIRouter(tags=["version"], prefix="/version")


@router.get("")
async def version() -> str:
    return "0.0.3"
