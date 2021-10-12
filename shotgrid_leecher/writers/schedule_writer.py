from pymongo.collection import Collection

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.commands import ScheduleShotgridBatchCommand
from shotgrid_leecher.record.enums import DbName, DbCollection


def _collection(collection: DbCollection) -> Collection:
    return (
        conn.get_db_client()
        .get_database(DbName.SCHEDULE.value)
        .get_collection(collection.value)
    )


def request_scheduling(command: ScheduleShotgridBatchCommand) -> None:
    projects_table = _collection(DbCollection.SCHEDULE_PROJECTS)
    query = {"$set": {"command": command.to_dict()}}
    projects_table.update_one(
        {"_id": command.project_name},
        query,
        upsert=True,
    )
