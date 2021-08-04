from typing import List, Dict, Any

import shotgrid_leecher.utils.connectivity as conn


def get_newest_created_asset_id() -> int:
    db = conn.get_db_client()
    count = db.openpype_shotgrid.new_asset_events.count()
    if count == 0:
        return 0
    return 0

