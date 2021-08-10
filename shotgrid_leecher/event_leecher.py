import shotgrid_leecher.repository.asset_events_repo as asset_events_repo
from shotgrid_leecher.domain.asset_domain import save_new_asset_events
from shotgrid_leecher.record.enums import (
    ShotgridEvents,
)
from shotgrid_leecher.utils.connectivity import get_shotgrid_client


async def get_recent_events() -> None:
    save_new_asset_events(None)
    print(
        asset_events_repo.get_last_created_event_id(ShotgridEvents.NEW_ASSET)
    )
    print(await asset_events_repo.get_newest_created_asset_id())
    shotgrid = get_shotgrid_client()
    filters = [
        ["id", "greater_than", 100],
        ["event_type", "is", "Shotgun_Asset_New"],
    ]
    fields = [
        "id",
        "event_type",
        "attribute_name",
        "meta",
        "entity",
        "user",
        "project",
        "session_uuid",
        "created_at",
    ]
    order = [{"column": "id", "direction": "asc"}]
    events = shotgrid.find(
        "EventLogEntry",
        filters,
        fields,
        order,
        limit=100,
    )
    print(events)
    pass
