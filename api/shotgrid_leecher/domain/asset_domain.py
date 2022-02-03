from typing import Sequence

from record.enums import EventTables
from record.new_event_commands import (
    NewEventCommand,
)
from record.results import InsertionResult
from utils import connectivity as conn


def save_new_asset_events(
    new_asset_commands: Sequence[NewEventCommand],
) -> InsertionResult:
    data = [x.to_dict() for x in new_asset_commands]
    result = conn.get_collection(EventTables.ASSET_EVENTS).insert_many(data)
    return InsertionResult(result.acknowledged, list(result.inserted_ids))
