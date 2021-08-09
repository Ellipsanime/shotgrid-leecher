import datetime
import json
from dataclasses import dataclass
from typing import Any, Dict

from shotgrid_leecher.record.shotgrid_project import ShotgridProject
from shotgrid_leecher.record.shotgrid_user import ShotgridUser
from shotgrid_leecher.utils.encoders import DataclassJSONEncoder


@dataclass(frozen=True)
class NewAssetEvent:
    shotgrid_id: int
    shotgrid_name: str
    shotgrid_creation_date: datetime
    shotgrid_user: ShotgridUser
    shotgrid_project: ShotgridProject
    type: str = "New_Asset_Event"

    def get_unique_id(self) -> str:
        return "".join(
            [
                self.shotgrid_project.name,
                "/",
                self.shotgrid_name,
            ]
        )
        # return hashlib.sha256(id_data.encode("utf-8")).hexdigest()

    def to_json(self) -> str:
        return json.dumps(self, cls=DataclassJSONEncoder)

    def to_dict(self) -> Dict[str, Any]:
        # TODO use more optimized way to convert dataclass to dict struct
        return json.loads(self.to_json())
