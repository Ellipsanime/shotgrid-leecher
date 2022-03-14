import validators
from fastapi import APIRouter, HTTPException

from shotgrid_leecher.record.queries import ShotgridFetchUserProjectLinksQuery
from shotgrid_leecher.repository import user_repo

router = APIRouter(tags=["user"], prefix="/user")


@router.get("/{email}/project-user-links")
async def project_user_links(email: str):
    if not validators.email(email):
        raise HTTPException(
            status_code=400,
            detail=f"Wrong email {email} format",
        )
    query = ShotgridFetchUserProjectLinksQuery(email)
    return user_repo.fetch_project_user_links(query)
