from typing import List, Any, Dict, Optional

import attr
import cattr
from bson import ObjectId

from shotgrid_leecher.record.enums import AvalonType


@attr.s(auto_attribs=True, frozen=True)
class AvalonProjectData:
    clipIn: int = 1
    clipOut: int = 1
    fps: float = 25.0
    frameEnd: int = 0
    frameStart: int = 0
    handleEnd: int = 0
    handleStart: int = 0
    pixelAspect: float = 0
    resolutionHeight: int = 0
    resolutionWidth: int = 0
    tools_env: List[Any] = []
    library_project: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return attr.asdict(self)

    @staticmethod
    def from_dict(raw_dic: Dict[str, Any]) -> "AvalonProjectData":
        return cattr.structure(raw_dic, AvalonProjectData)


@attr.s(auto_attribs=True, frozen=True)
class AvalonProject:
    id: str
    name: str
    data: AvalonProjectData
    config: Dict[str, Any]
    type: str = AvalonType.PROJECT.value
    schema: str = "openpype:project-3.0"

    def object_id(self) -> ObjectId:
        return ObjectId(self.id)

    def to_dict(self) -> Dict[str, Any]:
        return attr.asdict(self)

    @staticmethod
    def from_dict(raw_dic: Dict[str, Any]) -> Optional["AvalonProject"]:
        if not raw_dic:
            return None
        dic = {
            **{k: v for k, v in raw_dic.items() if k != "_id"},
            "id": str(raw_dic["_id"]),
            "data": raw_dic.get("data", dict()),
        }
        return cattr.structure(dic, AvalonProject)
