from datetime import datetime
from typing import Dict, Any, List

from pymongo.collection import Collection

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.commands import (
    ScheduleShotgridBatchCommand,
    LogBatchUpdateCommand,
)
from shotgrid_leecher.record.enums import DbName, DbCollection
from shotgrid_leecher.utils.logger import get_logger

_LOG = get_logger(__name__.split(".")[-1])


def _collection(collection: DbCollection) -> Collection:
    return (
        conn.get_db_client()
        .get_database(DbName.SCHEDULE.value)
        .get_collection(collection.value)
    )


def queue_requests(
    commands: List[ScheduleShotgridBatchCommand],
) -> Dict[str, Any]:
    now = datetime.utcnow().timestamp()
    queue_table = _collection(DbCollection.SCHEDULE_QUEUE)
    documents = [
        {"command": x.to_dict(), "created_at": now + i}
        for x, i in zip(commands, range(len(commands)))
    ]
    return queue_table.insert_many(documents)


def request_scheduling(
    command: ScheduleShotgridBatchCommand,
) -> Dict[str, Any]:
    projects_table = _collection(DbCollection.SCHEDULE_PROJECTS)
    query = {"$set": {"command": command.to_dict()}}
    return projects_table.update_one(
        {"_id": command.project_name},
        query,
        upsert=True,
    )


def log_batch_result(command: LogBatchUpdateCommand) -> Dict[str, Any]:
    logs_table = _collection(DbCollection.SCHEDULE_LOGS)
    _LOG.debug(f"log batch result: {command}")
    return logs_table.insert_one(command.to_dict())
