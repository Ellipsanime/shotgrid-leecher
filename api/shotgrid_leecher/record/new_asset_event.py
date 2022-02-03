import datetime
import json
from typing import Any, Dict

import attr

from record.enums import ShotgridEvents
from record.shotgrid_subtypes import (
    ShotgridProject,
    ShotgridUser,
    ShotgridEntity,
)
from utils.encoders import DataclassJSONEncoder


@attr.s(auto_attribs=True, frozen=True)
class NewAssetEvent:
    shotgrid_id: int
    shotgrid_name: str
    shotgrid_creation_date: datetime.datetime
    shotgrid_user: ShotgridUser
    shotgrid_project: ShotgridProject
    shotgrid_entity: ShotgridEntity
    type: str = ShotgridEvents.NEW_ASSET.value

    def get_unique_id(self) -> str:
        return "".join(
            [
                self.shotgrid_project.name,
                "/",
                self.shotgrid_name,
                "/",
                self.type,
            ]
        )

    def to_json(self) -> str:
        return json.dumps(self, cls=DataclassJSONEncoder)

    def to_dict(self) -> Dict[str, Any]:
        # TODO use more optimized way to convert dataclass to dict struct
        return json.loads(self.to_json())
