import shotgrid_leecher.mapper.asset_events_mapper as events_mapper
import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.enums import EventTables, ShotgridEvents


async def get_newest_created_asset_id(db=conn.get_db_client()) -> int:
    count = await db.openpype_shotgrid.new_asset_events.count()
    if count == 0:
        return 0
    return 0


def get_last_processed_event_id(event: ShotgridEvents) -> int:
    entry = conn.get_collection(EventTables.EVENT_STATUS).find_one(
        {"_id": ShotgridEvents.NEW_ASSET.value}
    )
    if not entry:
        return 0
    return events_mapper.event_status_from_dict(entry).last_processed_event_id
