from typing import Sequence

from shotgrid_leecher.record.enums import EventTables
from shotgrid_leecher.record.new_event_commands import (
    NewEventCommand,
)
from shotgrid_leecher.record.results import InsertionResult
from shotgrid_leecher.utils import connectivity as conn


def save_new_asset_events(
    new_asset_commands: Sequence[NewEventCommand],
) -> InsertionResult:
    data = [x.to_dict() for x in new_asset_commands]
    result = conn.get_collection(EventTables.ASSET_EVENTS).insert_many(data)
    return InsertionResult(result.acknowledged, list(result.inserted_ids))
