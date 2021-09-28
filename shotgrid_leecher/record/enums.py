from enum import Enum, unique


@unique
class DbName(Enum):
    AVALON = "avalon"
    INTERMEDIATE = "shotgrid_openpype"


@unique
class ShotgridTypes(Enum):
    PROJECT = "Project"
    ASSET = "Asset"
    SHOT = "Shot"
    EPISODE = "Episode"
    SEQUENCE = "Sequence"
    TASK = "Task"
    GROUP = "Group"


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
