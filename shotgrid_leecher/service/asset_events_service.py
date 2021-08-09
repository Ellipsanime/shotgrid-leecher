from toolz import pipe
from toolz.curried import (
    map as select,
    filter as where,
)

import shotgrid_leecher.domain.asset_domain as asset_domain
import shotgrid_leecher.mapper.asset_events_mapper as asset_events_mapper
import shotgrid_leecher.repository.asset_events_repo as asset_events_repo
import shotgrid_leecher.repository.shotgrid_events_repo as shotgrid_events_repo
from shotgrid_leecher.record.enums import (
    ShotgridEvents,
    EventTypes,
    EventStatuses,
)


def get_recent_events() -> None:
    last_id = asset_events_repo.get_last_processed_event_id(
        ShotgridEvents.NEW_ASSET,
    )
    return pipe(
        shotgrid_events_repo.get_recent_events(
            ShotgridEvents.NEW_ASSET,
            last_id,
        ),
        where(lambda x: x.get("entity")),
        select(asset_events_mapper.new_asset_event_from_dict),
        select(
            asset_events_mapper.new_event_command_from_event(
                EventTypes.CREATION, EventStatuses.INIT,
            )
        ),
        asset_domain.save_new_asset_events,
        # TODO save logic goes here ...
        list,
    )


# def _save_events(events: )
