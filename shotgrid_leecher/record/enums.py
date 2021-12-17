from enum import Enum, unique
from typing import List

from shotgrid_leecher.utils.functional import try_or


@unique
class QueryStringType(Enum):
    STR = str
    INT = int
    FLOAT = float

    @staticmethod
    def from_param(type_name: str) -> "QueryStringType":
        if not type_name:
            return QueryStringType.STR
        return try_or(
            lambda: QueryStringType[type_name.strip().upper()],
            QueryStringType.STR,
        )


@unique
class DbName(Enum):
    AVALON = "avalon"
    INTERMEDIATE = "shotgrid_openpype"
    SCHEDULE = "shotgrid_schedule"


@unique
class DbCollection(Enum):
    SCHEDULE_PROJECTS = "projects"
    SCHEDULE_QUEUE = "queue"
    SCHEDULE_LOGS = "logs"


@unique
class AvalonType(Enum):
    PROJECT = "project"
    ASSET = "asset"


@unique
class ShotgridType(Enum):
    PROJECT = "Project"
    ASSET = "Asset"
    LINKED_ENTITY = "LinkedEntity"
    SHOT = "Shot"
    EPISODE = "Episode"
    SEQUENCE = "Sequence"
    GROUP = "Group"
    TASK = "Task"
    STEP = "Step"
    ASSET_TO_SHOT_LINK = "AssetShotConnection"
    SHOT_TO_SHOT_LINK = "ShotShotConnection"
    ASSET_TO_ASSET_LINK = "AssetAssetConnection"

    @staticmethod
    def middle_types() -> List["ShotgridType"]:
        return [
            ShotgridType.GROUP,
            ShotgridType.ASSET,
            ShotgridType.SHOT,
            ShotgridType.EPISODE,
            ShotgridType.SEQUENCE,
        ]

    @staticmethod
    def middle_names() -> List[str]:
        return [x.value for x in ShotgridType.middle_types()]


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
    SEQUENCE_EPISODE = "sequence_episode"
    CUT_DURATION = "cut_duration"
    FRAME_RATE = "frame_rate"
    CUT_IN = "cut_in"
    CUT_OUT = "cut_out"
    HEAD_IN = "head_in"
    HEAD_OUT = "head_out"
    TAIL_IN = "tail_in"
    TAIL_OUT = "tail_out"
    CODE = "code"
    TYPE = "type"
    TASKS = "tasks"
    ASSET_TYPE = "asset_type"
    SHORT_NAME = "short_name"
    ASSETS = "assets"
    PARENTS = "parents"
    CACHED_DISPLAY_NAME = "cached_display_name"
    LINK_QUANTITY = "quantity"
    LINK_SHOT_ID = "link_shot_id"
    LINK_ASSET_ID = "link_asset_id"
    LINK_PARENT_ID = "link_parent_id"
    LINK_PARENT_SHOT_ID = "link_parent_shot_id"

    def to_db_key(self) -> str:
        return str(self.value).replace(".", "_")
