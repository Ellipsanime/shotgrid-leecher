from dataclasses import dataclass
from typing import Dict

from shotgrid_leecher.record.enums import ShotgridEvents


@dataclass(frozen=True)
class EventStatus:
    id: ShotgridEvents
    last_processed_event_id: int

    def to_find_by_id_filter(self) -> Dict[str, str]:
        return {"_id": self.id.value}

    def to_update_query(self) -> Dict[str, int]:
        return {"last_processed_event_id": self.last_processed_event_id}

    def copy_with(self, last_processed_event_id: int) -> "EventStatus":
        return EventStatus(
            self.id, last_processed_event_id=last_processed_event_id,
        )
