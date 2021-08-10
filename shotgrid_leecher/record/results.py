from dataclasses import dataclass
from typing import List, Any


@dataclass
class InsertionResult:
    acknowledged: bool
    inserted_ids: List[Any]

