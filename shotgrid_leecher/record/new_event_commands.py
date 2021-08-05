from dataclasses import dataclass
from typing import Union, List

from toolz import pipe
from toolz.curried import (
    map as select,
)

from shotgrid_leecher.record.enums import EventType, EventStatus
from shotgrid_leecher.record.new_asset_event import NewAssetEvent

AnyEvent = Union[NewAssetEvent]


@dataclass(frozen=True)
class NewEventCommand:
    event_type: EventType
    event_status: EventStatus
    event: AnyEvent


@dataclass(frozen=True)
class NewEventsCommand:
    # https://blog.insiderattack.net/implementing-event-sourcing-and-cqrs-pattern-with-mongodb-66991e7b72be
    event_type: EventType
    event_status: EventStatus
    events: List[AnyEvent]

    def to_list(self) -> List[NewEventCommand]:
        return pipe(
            self.events,
            select(
                lambda x: NewEventCommand(
                    self.event_type, self.event_status, x
                )
            ),
            list,
        )
