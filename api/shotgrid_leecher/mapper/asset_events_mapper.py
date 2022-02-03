from datetime import datetime
from typing import Dict, Any, cast

from toolz import get_in, curry

from record.enums import EventTypes
from record.new_asset_event import NewAssetEvent
from record.new_event_commands import NewEventCommand
from record.shotgrid_subtypes import (
    ShotgridProject,
    ShotgridUser,
    ShotgridEntity,
)


def new_asset_event_from_dict(dic: Dict[str, Any]) -> NewAssetEvent:
    project = ShotgridProject(**cast(Dict[str, Any], dic.get("project")))
    user = ShotgridUser(**cast(Dict[str, Any], dic.get("user")))
    entity = ShotgridEntity(**cast(Dict[str, Any], dic.get("entity")))
    return NewAssetEvent(
        int(str(dic.get("id"))),
        get_in(["entity", "name"], dic),
        datetime.fromisoformat(str(dic.get("created_at", datetime.now()))),
        user,
        project,
        entity,
    )


@curry
def new_event_command_from_event(
    event_type: EventTypes, event: NewAssetEvent
) -> NewEventCommand:
    return NewEventCommand(
        event.get_unique_id(),
        event_type,
        event,
    )
