from dataclasses import dataclass
from datetime import datetime
from typing import Union, List, Dict, Any

from toolz import pipe
from toolz.curried import (
    map as select,
)

from shotgrid_leecher.record.enums import EventTypes
from shotgrid_leecher.record.new_asset_event import NewAssetEvent

AnyEvent = Union[NewAssetEvent]


@dataclass(frozen=True)
class NewEventCommand:
    id: str
    event_type: EventTypes
    event: AnyEvent

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": f"{self.id}/{self.event_type}",
            "event_type": self.event_type,
            "event_data": self.event.to_dict(),
            "datetime": datetime.utcnow().isoformat(),
        }


@dataclass(frozen=True)
class NewEventsCommand:
    event_type: EventTypes
    events: List[AnyEvent]

    def to_list(self) -> List[NewEventCommand]:
        return pipe(
            self.events,
            select(
                lambda x: NewEventCommand(
                    x.get_unique_id(),
                    self.event_type,
                    x,
                )
            ),
            list,
        )
