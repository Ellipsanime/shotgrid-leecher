from typing import Dict, Any
import dacite as converter
from toolz import get_in, curry

from shotgrid_leecher.record.enums import EventTypes
from shotgrid_leecher.record.new_asset_event import NewAssetEvent
from shotgrid_leecher.record.new_event_commands import NewEventCommand
from shotgrid_leecher.record.shotgrid_subtypes import (
    ShotgridProject,
    ShotgridUser,
    ShotgridEntity,
)


def new_asset_event_from_dict(dic: Dict[str, Any]) -> NewAssetEvent:
    project = converter.from_dict(ShotgridProject, dic.get("project"))
    user = converter.from_dict(ShotgridUser, dic.get("user"))
    entity = converter.from_dict(ShotgridEntity, dic.get("entity"))
    return NewAssetEvent(
        int(dic.get("id")),
        get_in(["entity", "name"], dic),
        dic.get("created_at"),
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
        event_type.value,
        event,
    )
