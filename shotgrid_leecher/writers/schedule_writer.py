from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from motor.motor_asyncio import AsyncIOMotorCollection

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.commands import (
    ScheduleShotgridBatchCommand,
    LogBatchUpdateCommand,
)
from shotgrid_leecher.record.enums import DbName, DbCollection
from shotgrid_leecher.utils.logger import get_logger

_LOG = get_logger(__name__.split(".")[-1])


def _collection(collection: DbCollection) -> AsyncIOMotorCollection:
    return (
        conn.get_async_db_client()
        .get_database(DbName.SCHEDULE.value)
        .get_collection(collection.value)
    )


async def queue_requests(
    commands: List[ScheduleShotgridBatchCommand],
) -> Dict[str, Any]:
    now = datetime.utcnow()
    queue_table = _collection(DbCollection.SCHEDULE_QUEUE)
    documents = [
        {
            "command": x.to_dict(),
            "created_at": now + timedelta(seconds=i * 0.01),
        }
        for x, i in zip(commands, range(len(commands)))
    ]
    return await queue_table.insert_many(documents)


async def request_scheduling(
    command: ScheduleShotgridBatchCommand,
) -> Dict[str, Any]:
    projects_table = _collection(DbCollection.SCHEDULE_PROJECTS)
    query = {"$set": {"command": command.to_dict()}}
    return await projects_table.update_one(
        {"_id": command.project_name},
        query,
        upsert=True,
    )


async def dequeue_request() -> Optional[ScheduleShotgridBatchCommand]:
    queue_table = _collection(DbCollection.SCHEDULE_QUEUE)
    raw = await queue_table.find_one_and_delete({}, sort=[("created_at", 1)])
    if not raw:
        return None
    _LOG.debug(
        f"Pick project {raw['command']['project_name']}, at {raw['created_at']}"
    )
    return ScheduleShotgridBatchCommand.from_dict(raw["command"])


async def log_batch_result(command: LogBatchUpdateCommand) -> Dict[str, Any]:
    logs_table = _collection(DbCollection.SCHEDULE_LOGS)
    _LOG.debug(f"log batch result: {command}")
    return await logs_table.insert_one(command.to_dict())
