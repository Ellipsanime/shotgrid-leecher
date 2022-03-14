from enum import Enum, unique
from typing import List, Any, Dict

import attr


@attr.s(auto_attribs=True, frozen=True)
class DeletionResult:
    deleted_count: int


@attr.s(auto_attribs=True, frozen=True)
class InsertionResult:
    acknowledged: bool
    inserted_ids: List[Any]


@attr.s(auto_attribs=True, frozen=True)
class BatchCheckResult:
    status: str


@attr.s(auto_attribs=True, frozen=True)
class GroupAndCountResult:
    name: str
    count: int

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "GroupAndCountResult":
        return GroupAndCountResult(dic["_id"], dic["count"])


@unique
class ScheduleResult(Enum):
    FAILURE = "Failure"
    OK = "Ok"


@unique
class BatchResult(Enum):
    FAILURE = "Failure"
    NO_SHOTGRID_HIERARCHY = "No_Shotgrid_Hierarchy"
    WRONG_PROJECT_NAME = "Project_Names_Differres"
    OK = "Ok"


@unique
class LogType(Enum):
    SCHEDULE = "Schedule"
    BATCH = "Batch"
