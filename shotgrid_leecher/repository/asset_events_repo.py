import shotgrid_leecher.utils.connectivity as conn


async def get_newest_created_asset_id() -> int:
    db = conn.get_async_db_client()
    count = await db.openpype_shotgrid.new_asset_events.count()
    if count == 0:
        return 0
    return 0

