from typing import Any

from shotgrid_leecher.record.commands import (
    UpsertShotgridCredentialsCommand,
    DeleteShotgridCredentialsCommand,
)
from shotgrid_leecher.record.leecher_structures import ShotgridCredentials
from shotgrid_leecher.record.results import DeletionResult
from shotgrid_leecher.writers import config_writer


def upsert_credentials(credentials: ShotgridCredentials) -> Any:
    command = UpsertShotgridCredentialsCommand(credentials)
    config_writer.upsert_credentials(command)


def delete_credentials(shotgrid_url: str) -> DeletionResult:
    command = DeleteShotgridCredentialsCommand(shotgrid_url)
    return DeletionResult(
        config_writer.delete_credentials(command).deleted_count
    )
