from toolz import pipe

import shotgrid_leecher.mapper.asset_events_mapper as asset_events_mapper
import shotgrid_leecher.repository.asset_events_repo as asset_events_repo
import shotgrid_leecher.repository.shotgrid_events_repo as shotgrid_events_repo
from shotgrid_leecher.record.enums import ShotgridEvent
from toolz.curried import (
    map as select,
)


def get_recent_events() -> None:
    last_id = asset_events_repo.get_newest_created_asset_id()
    pipe(
        shotgrid_events_repo.get_recent_events(
            ShotgridEvent.NEW_ASSET,
            last_id,
        ),
        select(asset_events_mapper.new_asset_event_from_dict),
        select(lambda x: x.to_dict()),
    )
