import json
from dataclasses import dataclass

from shotgrid_leecher.utils.encoders import DataclassJSONEncoder


@dataclass(frozen=True)
class GenericSubtype:
    id: int
    name: str
    type: str

    def to_json(self) -> str:
        return json.dumps(self, cls=DataclassJSONEncoder)


@dataclass(frozen=True)
class ShotgridUser(GenericSubtype):
    pass


@dataclass(frozen=True)
class ShotgridProject(GenericSubtype):
    pass


@dataclass(frozen=True)
class ShotgridEntity(GenericSubtype):
    pass

