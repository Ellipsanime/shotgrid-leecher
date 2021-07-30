from enum import Enum, unique


@unique
class ShotgridEvent(Enum):
    NEW_ASSET = "Shotgun_Asset_New"


@unique
class ShotgridEventEntry(Enum):
    EVENT_ENTRY = "EventLogEntry"
