from dataclasses import dataclass
from typing import List, Any


@dataclass(frozen=True)
class InsertionResult:
    acknowledged: bool
    inserted_ids: List[Any]


@dataclass(frozen=True)
class BatchCheckResult:
    status: str
