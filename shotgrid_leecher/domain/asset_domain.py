import random
from typing import Dict

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.enums import EventTables, ShotgridEvents
from shotgrid_leecher.record.new_event_commands import NewEventsCommand


def save_new_asset_events(new_assets_command: NewEventsCommand) -> Dict:
    db = conn.get_db_client()

    return db.openpype_shotgrid[EventTables.EVENT_STATUS.value].update_one(
        {"_id": ShotgridEvents.NEW_ASSET.value},
        {"$set": {"last_processed_event_id": random.randint(1, 20)}},
        upsert=True,
    )
    # conn.get_async_db_client().openpype_shotgrid[EventTables.ASSET_EVENTS.value]
