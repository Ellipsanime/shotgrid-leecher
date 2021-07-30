import json
from dataclasses import dataclass
from typing import Optional, Any, Dict

from shotgrid_leecher.record.shotgrid_project import ShotgridProject
from shotgrid_leecher.record.shotgrid_user import ShotgridUser
from shotgrid_leecher.utils.encoders import DataclassJSONEncoder


@dataclass(frozen=True)
class NewAssetEvent:
    shotgrid_id: Optional[int]
    shotgrid_entity_id: Optional[int]
    shotgrid_session_uuid: Optional[str]
    shotgrid_user: ShotgridUser
    shotgrid_project: ShotgridProject
    type: str = "New_Asset_Event"

    def to_json(self) -> str:
        return json.dumps(self, cls=DataclassJSONEncoder)

    def to_dict(self) -> Dict[str, Any]:
        # TODO use more optimized way to convert dataclass to dict struct
        return json.loads(self.to_json())
