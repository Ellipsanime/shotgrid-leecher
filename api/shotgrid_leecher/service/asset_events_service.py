from toolz import pipe
from toolz.curried import (
    map as select,
    filter as where,
)

import domain.asset_domain as asset_domain
import mapper.asset_events_mapper as asset_events_mapper
import repository.asset_events_repo as asset_events_repo
import repository.shotgrid_events_repo as shotgrid_events_repo
from record.enums import (
    ShotgridEvents,
    EventTypes,
)


def get_recent_events() -> None:
    last_id = asset_events_repo.get_last_created_event_id(
        ShotgridEvents.NEW_ASSET,
    )
    result = pipe(
        shotgrid_events_repo.get_recent_events(
            ShotgridEvents.NEW_ASSET,
            last_id,
        ),
        where(lambda x: x.get("entity")),
        select(asset_events_mapper.new_asset_event_from_dict),
        select(
            asset_events_mapper.new_event_command_from_event(
                EventTypes.INITIALIZED,
            )
        ),
        asset_domain.save_new_asset_events,
    )
    print(result)


# def _save_events(events: )
