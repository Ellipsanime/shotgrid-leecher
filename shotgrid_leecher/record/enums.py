from enum import Enum, unique


@unique
class ShotgridEvent(Enum):
    NEW_ASSET = "Shotgun_Asset_New"


@unique
class EventTables(Enum):
    ASSET_EVENTS = "asset_events"


@unique
class EventType(Enum):
    CREATION = "Creation"
    UPDATE = "Update"
    DELETE = "Delete"


@unique
class EventStatus(Enum):
    INIT = "Initialized"
    ASSIGNED = "Assigned"
    DONE = "Done"


@unique
class ShotgridEventEntry(Enum):
    EVENT_ENTRY = "EventLogEntry"
