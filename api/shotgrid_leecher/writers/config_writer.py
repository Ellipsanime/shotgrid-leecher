from datetime import datetime

from pymongo import UpdateOne, DeleteOne
from pymongo.results import BulkWriteResult

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.commands import (
    UpsertShotgridCredentialsCommand,
    DeleteShotgridCredentialsCommand,
)
from shotgrid_leecher.record.enums import DbName, DbCollection
from shotgrid_leecher.utils.logger import get_logger

_LOG = get_logger(__name__.split(".")[-1])

_collection = conn.db_collection(DbName.LEECHER)


def delete_credentials(
    command: DeleteShotgridCredentialsCommand,
) -> BulkWriteResult:
    credentials_table = _collection(DbCollection.SHOTGRID_CREDENTIALS)
    documents = [DeleteOne({"_id": command.shotgrid_url})]
    return credentials_table.bulk_write(documents)


def upsert_credentials(
    command: UpsertShotgridCredentialsCommand,
) -> BulkWriteResult:
    credentials_table = _collection(DbCollection.SHOTGRID_CREDENTIALS)
    documents = [
        UpdateOne(
            {"_id": command.credentials.shotgrid_url},
            {
                "$set": {
                    "script_name": command.credentials.script_name,
                    "script_key": command.credentials.script_key,
                    "datetime": datetime.now(),
                }
            },
            upsert=True,
        )
    ]
    return credentials_table.bulk_write(documents)
