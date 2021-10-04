import dataclasses
import json
from datetime import datetime, date
from typing import Any

import attr
from bson import json_util


class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, entity: Any) -> Any:
        if attr.has(type(entity)):
            return attr.asdict(entity)
        if dataclasses.is_dataclass(entity):
            return dataclasses.asdict(entity)
        if isinstance(entity, (datetime, date)):
            return entity.isoformat()
        return json_util.default(entity)

