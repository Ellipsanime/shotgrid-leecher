import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.enums import EventTables
from shotgrid_leecher.record.new_event_commands import NewEventsCommand


async def save_new_asset_events(new_assets_command: NewEventsCommand) -> None:
    conn.get_async_db_client().openpype_shotgrid[EventTables.ASSET_EVENTS].insert
