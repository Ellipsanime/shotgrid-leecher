from enum import Enum, unique


@unique
class ShotgridEvents(Enum):
    NEW_ASSET = "Shotgun_Asset_New"


@unique
class EventTables(Enum):
    ASSET_EVENTS = "asset_events"
    EVENT_STATUS = "event_status"


@unique
class EventTypes(Enum):
    INITIALIZED = "Initialized"
    ASSIGNED = "Assigned"
    DONE = "Done"


@unique
class ShotgridEventEntries(Enum):
    EVENT_ENTRY = "EventLogEntry"
