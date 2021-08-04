from dataclasses import dataclass
from typing import Union, List

from shotgrid_leecher.record.enums import EventType, EventStatus
from shotgrid_leecher.record.new_asset_event import NewAssetEvent


@dataclass(frozen=True)
class NewEventCommand:
    event_type: EventType
    event_status: EventStatus
    event: Union[NewAssetEvent]


@dataclass(frozen=True)
class NewEventsCommand:
    # https://blog.insiderattack.net/implementing-event-sourcing-and-cqrs-pattern-with-mongodb-66991e7b72be
    event_type: EventType
    events: List[Union[NewAssetEvent]]
