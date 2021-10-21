from typing import List

from motor.motor_asyncio import AsyncIOMotorCollection

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.commands import (
    ScheduleShotgridBatchCommand,
)
from shotgrid_leecher.record.enums import DbName, DbCollection
from shotgrid_leecher.record.results import GroupAndCountResult


def fetch_batch_commands(
    already_queued: List[str],
) -> List[ScheduleShotgridBatchCommand]:
    return [
        ScheduleShotgridBatchCommand.from_dict(x["command"])
        for x in _collection(DbCollection.SCHEDULE_PROJECTS).find(
            {"command.project_name": {"$nin": already_queued}}
        )
    ]


def group_batch_commands() -> List[GroupAndCountResult]:
    if not queue_size():
        return []
    group_by = {
        "$group": {"_id": "$command.project_name", "count": {"$sum": 1}}
    }
    groups = _collection(DbCollection.SCHEDULE_QUEUE).aggregate([group_by])
    return [GroupAndCountResult.from_dict(x) for x in list(groups)]


def queue_size() -> int:
    return _collection(DbCollection.SCHEDULE_QUEUE).count_documents({})


def count_projects() -> int:
    return _collection(DbCollection.SCHEDULE_PROJECTS).count_documents({})


def _collection(collection: DbCollection) -> AsyncIOMotorCollection:
    return (
        conn.get_db_client()
        .get_database(DbName.SCHEDULE.value)
        .get_collection(collection.value)
    )
