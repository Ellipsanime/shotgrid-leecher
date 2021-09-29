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


@unique
class ShotgridField(Enum):
    ENTITY = "entity"
    ID = "id"
    STEP = "step"
    CONTENT = "content"
    NAME = "name"
    SEQUENCE = "sequence"
    EPISODE = "episode"
    SEQUENCE_EPISODE = "sequence.episode"
    CUT_DURATION = "cut_duration"
    FRAME_RATE = "frame_rate"
    CODE = "code"
    ASSET_TYPE = "asset_type"
