import dataclasses
import json
from typing import Any, Dict


class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, entity: Any) -> Dict[str, Any]:
        if dataclasses.is_dataclass(entity):
            return dataclasses.asdict(entity)
        return super().default(entity)

