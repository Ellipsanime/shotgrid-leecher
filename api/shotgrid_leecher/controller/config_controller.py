from fastapi import APIRouter

import shotgrid_leecher.domain.config_domain as domain
from shotgrid_leecher.record.http_models import (
    ShotgridCredentialsModel,
    ShotgridUrlModel,
)
from shotgrid_leecher.record.leecher_structures import ShotgridCredentials

router = APIRouter(tags=["config"], prefix="/config")


@router.post("/credentials")
async def upsert_credentials(model: ShotgridCredentialsModel):
    credentials = ShotgridCredentials(
        model.shotgrid_url, model.script_name, model.script_key
    )
    domain.upsert_credentials(credentials)
    return {"result": "ok"}


@router.delete("/credentials")
async def delete_credentials(model: ShotgridUrlModel):
    domain.delete_credentials(model.shotgrid_url)
    return {"result": "ok"}
