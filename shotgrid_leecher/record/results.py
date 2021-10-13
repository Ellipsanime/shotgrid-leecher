from enum import Enum, unique
from typing import List, Any

import attr


@attr.s(auto_attribs=True, frozen=True)
class InsertionResult:
    acknowledged: bool
    inserted_ids: List[Any]


@attr.s(auto_attribs=True, frozen=True)
class BatchCheckResult:
    status: str


@unique
class BatchResult(Enum):
    FAILURE = -5
    NO_SHOTGRID_HIERARCHY = -1
    OK = 0
