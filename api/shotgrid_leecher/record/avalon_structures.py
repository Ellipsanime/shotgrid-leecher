from typing import List, Any, Dict, Optional

import attr
import cattr
from bson import ObjectId

from record.enums import AvalonType
from utils.strings import snakify_camel


@attr.s(auto_attribs=True, frozen=True)
class AvalonProjectData:
    clip_in: int = attr.ib(default=1)
    clip_out: int = attr.ib(default=1)
    fps: float = attr.ib(default=25.0)
    frame_end: int = attr.ib(default=0)
    frame_start: int = attr.ib(default=0)
    handle_end: int = attr.ib(default=0)
    handle_start: int = attr.ib(default=0)
    pixel_aspect: float = attr.ib(default=0)
    resolution_height: int = attr.ib(default=0)
    resolution_width: int = attr.ib(default=0)
    tools_env: List[Any] = attr.ib(default=[])
    library_project: bool = attr.ib(default=False)

    def to_dict(self) -> Dict[str, Any]:
        return attr.asdict(self)

    @staticmethod
    def from_dict(raw_dic: Dict[str, Any]) -> "AvalonProjectData":
        return cattr.structure(
            {snakify_camel(k): v for k, v in raw_dic.items()},
            AvalonProjectData,
        )


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
        }
        middle_state_structure = cattr.structure(dic, AvalonProject)
        data = AvalonProjectData.from_dict(raw_dic.get("data", dict()))
        return attr.evolve(middle_state_structure, data=data)
