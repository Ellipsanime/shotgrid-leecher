from typing import Dict, Any, List, Optional

import attr
import cattr
from bson import ObjectId

from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.utils.strings import avalonify_snake_case

Map = Dict[str, Any]

cattr.register_structure_hook(ObjectId, lambda v, _: ObjectId(str(v)))


@attr.s(auto_attribs=True, frozen=True)
class IntermediateParams:
    clip_in: int
    clip_out: int
    fps: float
    frame_end: int
    frame_start: int
    handle_end: int
    handle_start: int
    pixel_aspect: float
    resolution_height: int
    resolution_width: int
    tools_env: List[Any]

    def to_dict(self) -> Map:
        return attr.asdict(self)

    def to_avalonish_dict(self) -> Map:
        healthy_dic = self.to_dict()
        smoker_dic = {
            avalonify_snake_case(k): v for k, v in healthy_dic.items()
        }
        return smoker_dic


@attr.s(auto_attribs=True, frozen=True)
class IntermediateRow:
    id: str
    parent: str
    params: IntermediateParams
    src_id: Optional[int] = attr.attrib(None, init=False)
    code: Optional[str] = attr.attrib(None, init=False)
    type: ShotgridType = attr.attrib(init=False)
    object_id: Optional[ObjectId] = attr.attrib(init=False)

    def has_field(self, field: str):
        return field in attr.asdict(self, recurse=False).keys()

    def to_dict(self) -> Map:
        base_dict = {k: v for k, v in attr.asdict(self).items() if k != "id"}
        return {
            **base_dict,
            "_id": self.id,
            "type": self.type.value,
        }


@attr.s(auto_attribs=True, frozen=True)
class IntermediateGroup(IntermediateRow):
    type = ShotgridType.GROUP
    object_id: Optional[ObjectId] = attr.attrib(default=None)


@attr.s(auto_attribs=True, frozen=True)
class IntermediateAsset(IntermediateRow):
    src_id: int
    type = ShotgridType.ASSET
    object_id: Optional[ObjectId] = attr.attrib(default=None)


@attr.s(auto_attribs=True, frozen=True)
class IntermediateTask(IntermediateRow):
    task_type: str
    src_id: int
    type = ShotgridType.TASK
    object_id: Optional[ObjectId] = attr.attrib(default=None)


@attr.s(auto_attribs=True, frozen=True)
class IntermediateShot(IntermediateRow):
    src_id: int
    type = ShotgridType.SHOT
    object_id: Optional[ObjectId] = attr.attrib(default=None)


@attr.s(auto_attribs=True, frozen=True)
class IntermediateEpisode(IntermediateRow):
    src_id: int
    type = ShotgridType.EPISODE
    object_id: Optional[ObjectId] = attr.attrib(default=None)


@attr.s(auto_attribs=True, frozen=True)
class IntermediateSequence(IntermediateRow):
    src_id: int
    type = ShotgridType.SEQUENCE
    object_id: Optional[ObjectId] = attr.attrib(default=None)


@attr.s(auto_attribs=True, frozen=True)
class IntermediateProjectStep:
    code: str
    short_name: str

    def to_dict(self) -> Map:
        return {
            self.code: {
                "short_name": self.short_name,
            }
        }

    @staticmethod
    def from_dict(raw_dic: Map) -> "IntermediateProjectStep":
        code = list(raw_dic.keys())[0]
        short_name = raw_dic[code]["short_name"]
        return IntermediateProjectStep(code=code, short_name=short_name)


@attr.s(auto_attribs=True, frozen=True)
class IntermediateProjectConfig:
    steps: List[IntermediateProjectStep] = []

    def to_dict(self) -> Map:
        return {"steps": [x.to_dict() for x in self.steps]}

    @staticmethod
    def from_dict(raw_dic: Optional[Map]) -> "IntermediateProjectConfig":
        if not raw_dic:
            return IntermediateProjectConfig()
        return IntermediateProjectConfig(
            [
                IntermediateProjectStep.from_dict(x)
                for x in raw_dic.get("steps", [])
            ]
        )


@attr.s(auto_attribs=True, frozen=True)
class IntermediateProject(IntermediateRow):
    src_id: int
    code: str
    config: IntermediateProjectConfig
    object_id: Optional[ObjectId] = attr.attrib(default=None)
    parent: str = attr.attrib(init=False, default=None)
    type = ShotgridType.PROJECT

    @staticmethod
    def from_dict(raw_dic: Map) -> "IntermediateProject":
        config = IntermediateProjectConfig.from_dict(raw_dic.get("config"))
        dic: Map = {
            **raw_dic,
            "config": config,
        }
        return IntermediateProject(
            id=dic["id"],
            params=dic["params"],
            src_id=dic["src_id"],
            code=dic["code"],
            config=dic["config"],
            object_id=dic.get("object_id"),
        )
