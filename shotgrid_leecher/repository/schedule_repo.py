from typing import List

from motor.motor_asyncio import AsyncIOMotorCollection

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.commands import (
    ScheduleShotgridBatchCommand,
)
from shotgrid_leecher.record.enums import DbName, DbCollection
from shotgrid_leecher.record.results import GroupAndCountResult


async def fetch_batch_commands(
    already_queued: List[str],
) -> List[ScheduleShotgridBatchCommand]:
    return [
        ScheduleShotgridBatchCommand.from_dict(x["command"])
        async for x in _collection(DbCollection.SCHEDULE_PROJECTS).find(
            {"command.project_name": {"$nin": already_queued}}
        )
    ]


async def group_batch_commands() -> List[GroupAndCountResult]:
    if not await queue_size():
        return []
    group_by = {
        "$group": {"_id": "$command.project_name", "count": {"$sum": 1}}
    }
    groups = await _collection(DbCollection.SCHEDULE_QUEUE).aggregate(
        [group_by]
    )
    return [GroupAndCountResult.from_dict(x) for x in list(groups)]


async def queue_size() -> int:
    return await _collection(DbCollection.SCHEDULE_QUEUE).count_documents({})


async def count_projects() -> int:
    return await _collection(DbCollection.SCHEDULE_PROJECTS).count_documents(
        {}
    )


def _collection(collection: DbCollection) -> AsyncIOMotorCollection:
    return (
        conn.get_async_db_client()
        .get_database(DbName.SCHEDULE.value)
        .get_collection(collection.value)
    )
