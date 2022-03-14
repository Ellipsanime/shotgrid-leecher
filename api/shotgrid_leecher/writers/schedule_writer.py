from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from pymongo import UpdateOne

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.commands import (
    ScheduleShotgridBatchCommand,
    LogScheduleUpdateCommand,
    CancelBatchSchedulingCommand,
    CleanScheduleBatchLogsCommand,
)
from shotgrid_leecher.record.enums import DbName, DbCollection
from shotgrid_leecher.utils.logger import get_logger

_LOG = get_logger(__name__.split(".")[-1])

_collection = conn.db_collection(DbName.SCHEDULE)


def queue_requests(
    commands: List[ScheduleShotgridBatchCommand],
) -> Dict[str, Any]:
    now = datetime.now()
    queue_table = _collection(DbCollection.SCHEDULE_QUEUE)
    documents = [
        UpdateOne(
            {"_id": x.project_name},
            {
                "$set": {
                    "command": x.to_dict(),
                    "datetime": now + timedelta(seconds=i * 0.01),
                }
            },
            upsert=True,
        )
        for x, i in zip(commands, range(len(commands)))
    ]
    return queue_table.bulk_write(documents)


def request_scheduling(
    command: ScheduleShotgridBatchCommand,
) -> Dict[str, Any]:
    now = datetime.now()
    projects_table = _collection(DbCollection.SCHEDULE_PROJECTS)
    query = {"$set": {"command": command.to_dict(), "datetime": now}}
    return projects_table.update_one(
        {"_id": command.project_name},
        query,
        upsert=True,
    )


def dequeue_request() -> Optional[ScheduleShotgridBatchCommand]:
    queue_table = _collection(DbCollection.SCHEDULE_QUEUE)
    raw = queue_table.find_one_and_delete({}, sort=[("datetime", 1)])
    if not raw:
        return None
    _LOG.debug(
        f"Pick project {raw['command']['project_name']}, at {raw['datetime']}"
    )
    return ScheduleShotgridBatchCommand.from_dict(raw["command"])


def log_batch_result(command: LogScheduleUpdateCommand) -> Dict[str, Any]:
    logs_table = _collection(DbCollection.SCHEDULE_LOGS)
    _LOG.debug(f"log batch result: {command}")
    return logs_table.insert_one(command.to_dict())


def remove_scheduled_project(
    command: CancelBatchSchedulingCommand,
) -> Dict[str, Any]:
    project_table = _collection(DbCollection.SCHEDULE_PROJECTS)
    _LOG.debug(f"Remove scheduling for: {command.project_name}")
    result = project_table.delete_one({"_id": command.project_name})
    return {
        "deleted_count": result.deleted_count,
    }


def clean_schedule_batch_logs(
    command: CleanScheduleBatchLogsCommand,
) -> Dict[str, Any]:
    logs_table = _collection(DbCollection.SCHEDULE_LOGS)
    result = logs_table.delete_many(
        {"datetime": {"$lte": command.datetime_gt}}
    )
    _LOG.debug(f"Clean batch logs result: {result.raw_result}")
    return result
