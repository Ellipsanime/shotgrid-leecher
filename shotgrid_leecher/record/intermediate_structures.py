from typing import Optional, Dict, Any, List

import attr

from shotgrid_leecher.record.enums import ShotgridType

Map = Dict[str, Any]


@attr.s(auto_attribs=True, frozen=True)
class IntermediateRow:
    id: str
    parent: str
    type: ShotgridType = attr.attrib(init=False)

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
class IntermediateTopShot(IntermediateRow):
    type = ShotgridType.GROUP


@attr.s(auto_attribs=True, frozen=True)
class IntermediateTopAsset(IntermediateRow):
    type = ShotgridType.GROUP


@attr.s(auto_attribs=True, frozen=True)
class IntermediateAssetGroup(IntermediateRow):
    type = ShotgridType.GROUP


@attr.s(auto_attribs=True, frozen=True)
class IntermediateAsset(IntermediateRow):
    src_id: int
    type = ShotgridType.ASSET


@attr.s(auto_attribs=True, frozen=True)
class IntermediateTask(IntermediateRow):
    task_type: str
    src_id: int
    type = ShotgridType.TASK


@attr.s(auto_attribs=True, frozen=True)
class IntermediateShotParams:
    clip_in: Optional[int]
    clip_out: Optional[int]

    def to_dict(self) -> Map:
        return attr.asdict(self)


@attr.s(auto_attribs=True, frozen=True)
class IntermediateParams:
    fps: float
    tools_env: List[Any]

    def to_dict(self) -> Map:
        return attr.asdict(self)


@attr.s(auto_attribs=True, frozen=True)
class IntermediateShot(IntermediateRow):
    params: Optional[IntermediateShotParams]
    src_id: int
    type = ShotgridType.SHOT


@attr.s(auto_attribs=True, frozen=True)
class IntermediateEpisode(IntermediateRow):
    src_id: int
    type = ShotgridType.EPISODE


@attr.s(auto_attribs=True, frozen=True)
class IntermediateSequence(IntermediateRow):
    src_id: int
    type = ShotgridType.SEQUENCE


@attr.s(auto_attribs=True, frozen=True)
class IntermediateProject(IntermediateRow):
    src_id: int
    parent: str = attr.attrib(init=False, default=None)
    type = ShotgridType.PROJECT
