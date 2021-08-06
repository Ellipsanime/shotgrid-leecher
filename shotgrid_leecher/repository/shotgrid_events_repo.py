from typing import Any, List, Dict

import shotgrid_leecher.utils.connectivity as connectivity
from shotgrid_leecher.record.enums import ShotgridEvents, ShotgridEventEntries

DEFAULT_FIELDS = [
    "id",
    "event_type",
    "attribute_name",
    "meta",
    "entity",
    "user",
    "project",
    "session_uuid",
    "created_at",
]

DEFAULT_ORDER = [{"column": "id", "direction": "asc"}]

DEFAULT_LIMIT = 100


def _find_events(
    filters: List[List[str]], limit: int = 100
) -> List[Dict[str, Any]]:
    return connectivity.get_shotgrid_client().find(
        ShotgridEventEntries.EVENT_ENTRY.value,
        filters,
        DEFAULT_FIELDS,
        DEFAULT_ORDER,
        limit=limit,
    )


def get_recent_events(
    event: ShotgridEvents, last_id: int
) -> List[Dict[str, Any]]:
    filters = [
        ["id", "greater_than", last_id],
        ["event_type", "is", event.value],
    ]
    return _find_events(filters, DEFAULT_LIMIT)
