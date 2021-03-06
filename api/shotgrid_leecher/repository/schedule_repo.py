from typing import List, Dict, Any

from toolz import pipe, curry, compose
from toolz.curried import (
    map as select,
)

from shotgrid_leecher.record.commands import (
    ScheduleShotgridBatchCommand,
)
from shotgrid_leecher.record.enums import DbName, DbCollection
from shotgrid_leecher.record.leecher_structures import (
    ScheduleLog,
    ScheduleProject,
    ScheduleQueueItem,
    EnhancedScheduleProject,
)
from shotgrid_leecher.record.queries import FindEntityQuery
from shotgrid_leecher.record.results import GroupAndCountResult
from shotgrid_leecher.utils.connectivity import db_collection

_collection = db_collection(DbName.SCHEDULE)


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


def fetch_scheduled_logs(find_query: FindEntityQuery) -> List[ScheduleLog]:
    return [
        ScheduleLog.from_dict(x)
        for x in _fetch_all(find_query, DbCollection.SCHEDULE_LOGS)
    ]


def fetch_scheduled_queue(
    find_query: FindEntityQuery,
) -> List[ScheduleQueueItem]:
    return [
        ScheduleQueueItem.from_dict(x)
        for x in _fetch_all(find_query, DbCollection.SCHEDULE_QUEUE)
    ]


def fetch_scheduled_projects(
    find_query: FindEntityQuery,
) -> List[ScheduleProject]:
    return [
        ScheduleProject.from_dict(x)
        for x in _fetch_all(find_query, DbCollection.SCHEDULE_PROJECTS)
    ]


@curry
def _latest_logs_query(limit: int, project_name: str) -> FindEntityQuery:
    return FindEntityQuery(
        filter={"project_name": project_name},
        limit=limit,
        sort=[("datetime", -1)],
    )


def fetch_enhanced_projects(
    find_query: FindEntityQuery,
) -> List[EnhancedScheduleProject]:
    fetch_logs = compose(fetch_scheduled_logs, _latest_logs_query(5))
    return pipe(
        _fetch_all(find_query, DbCollection.SCHEDULE_PROJECTS),
        select(ScheduleProject.from_dict),
        select(
            lambda x: EnhancedScheduleProject.from_entities(
                x, fetch_logs(x.project_name)
            )
        ),
        list,
    )


def _fetch_all(
    find_query: FindEntityQuery,
    collection_kind: DbCollection,
) -> List[Dict[str, Any]]:
    cursor = _collection(collection_kind).find(
        find_query.filter,
        sort=find_query.sort,
        skip=find_query.skip_or_default(),
        limit=find_query.limit_or_default(),
    )
    return list(cursor)
