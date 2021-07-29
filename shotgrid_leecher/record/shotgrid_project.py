import json
from dataclasses import dataclass

from shotgrid_leecher.utils.encoders import DataclassJSONEncoder


@dataclass(frozen=True)
class ShotgridProject:
    id: int
    name: str
    type: str

    def to_json(self) -> str:
        return json.dumps(self, cls=DataclassJSONEncoder)
