from enum import Enum, unique


@unique
class ShotgridTypes(Enum):
    PROJECT = "Project"
    ASSET = "Asset"
    SHOT = "Shot"
    TASK = "Task"


@unique
class ShotgridEvents(Enum):
    NEW_ASSET = "Shotgun_Asset_New"


@unique
class EventTables(Enum):
    ASSET_EVENTS = "asset_events"
    VERSION_EVENTS = "version_events"


@unique
class EventTypes(Enum):
    INITIALIZED = "Initialized"
    ASSIGNED = "Assigned"
    DONE = "Done"


@unique
class ShotgridEventEntries(Enum):
    EVENT_ENTRY = "EventLogEntry"
