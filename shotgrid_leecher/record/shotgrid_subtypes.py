import json
from dataclasses import dataclass, asdict
from typing import Dict, Any

from dacite import from_dict

from shotgrid_leecher.utils.encoders import DataclassJSONEncoder


@dataclass(frozen=True)
class GenericSubtype:
    id: int
    name: str
    type: str

    def to_json(self) -> str:
        return json.dumps(self, cls=DataclassJSONEncoder)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ShotgridUser(GenericSubtype):
    pass


@dataclass(frozen=True)
class ShotgridProject(GenericSubtype):
    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "ShotgridProject":
        return from_dict(ShotgridProject, dic)


@dataclass(frozen=True)
class ShotgridEntity(GenericSubtype):
    pass
