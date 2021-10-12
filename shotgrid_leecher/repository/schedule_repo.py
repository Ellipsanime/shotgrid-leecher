from typing import List

from pymongo.collection import Collection

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.commands import ShotgridToAvalonBatchCommand
from shotgrid_leecher.record.enums import DbName, DbCollection


def fetch_batch_commands() -> List[ShotgridToAvalonBatchCommand]:
    return [
        ShotgridToAvalonBatchCommand.from_dict(x)
        for x in _collection().find({})
    ]


def _collection() -> Collection:
    return (
        conn.get_db_client()
        .get_database(DbName.SCHEDULE.value)
        .get_collection(DbCollection.SCHEDULE_PROJECTS.value)
    )
