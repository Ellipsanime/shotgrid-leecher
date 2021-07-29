from shotgrid_leecher.utils.connectivity import get_db_client


def get_newest_created_asset_id() -> int:
    db = get_db_client()
    count = db.shotgrid.new_asset_events.count()
    if count == 0:
        return 0
    return 0
