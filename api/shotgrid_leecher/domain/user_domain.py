from typing import Any

from pymongo.results import BulkWriteResult
from toolz import pipe
from toolz.curried import (
    map as select,
)

import shotgrid_leecher.repository.shotgrid_user_repo as shotgrid_repo
from shotgrid_leecher.record.commands import UpsertProjectUserLinksCommand
from shotgrid_leecher.record.leecher_structures import ShotgridCredentials
from shotgrid_leecher.record.queries import ShotgridFindUserProjectLinkQuery
from shotgrid_leecher.repository import config_repo
from shotgrid_leecher.utils.logger import get_logger
from shotgrid_leecher.writers import user_writer

_LOG = get_logger(__name__.split(".")[-1])


def _refill_project_user_links(
    credentials: ShotgridCredentials,
) -> BulkWriteResult:
    user_writer.delete_links_by_host_url(credentials.shotgrid_url)
    return pipe(
        credentials,
        ShotgridFindUserProjectLinkQuery,
        shotgrid_repo.find_linked_projects,
        UpsertProjectUserLinksCommand,
        user_writer.upsert_project_user_links,
    )


async def synchronize_project_user_links() -> Any:
    creds = config_repo.fetch_credentials()
    _LOG.debug(f"Synchronize project user links for {len(creds)} credentials")
    pipe(creds, select(_refill_project_user_links), list)
