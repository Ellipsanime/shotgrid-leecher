from typing import Dict, List, Any

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.enums import EventTables
from shotgrid_leecher.record.new_event_commands import (
    NewEventCommand,
)


def save_new_asset_events(
    new_asset_commands: List[NewEventCommand],
) -> Dict[str, Any]:
    db = conn.get_db_client()
    data = [x.to_dict() for x in new_asset_commands]
    return db.openpype_shotgrid[EventTables.ASSET_EVENTS.value].insert_many(
        data
    )
    # conn.get_async_db_client().openpype_shotgrid[EventTables.ASSET_EVENTS.value]
