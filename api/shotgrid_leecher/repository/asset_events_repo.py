from toolz import get_in

import utils.connectivity as conn
from record.enums import (
    EventTables,
    ShotgridEvents,
    EventTypes,
)


async def get_newest_created_asset_id(db=conn.get_db_client()) -> int:
    count = await db.openpype_shotgrid.new_asset_events.count()
    if count == 0:
        return 0
    return 0


def get_last_created_event_id(event: ShotgridEvents) -> int:
    path = "event_data.shotgrid_id"
    cursor = (
        conn.get_collection(EventTables.ASSET_EVENTS)
        .find(
            {
                "event_data.type": event.value,
                "event_type": EventTypes.INITIALIZED.value,
            }
        )
        .sort(path, -1)
        .limit(1)
    )
    if cursor.count(True) == 0:
        return 0
    return get_in(path.split("."), cursor.next(), 0)
