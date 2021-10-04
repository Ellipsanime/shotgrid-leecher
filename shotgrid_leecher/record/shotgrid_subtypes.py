import json
from dataclasses import field
from typing import Dict, Any

import attr

from shotgrid_leecher.record.enums import ShotgridType, ShotgridField
from shotgrid_leecher.utils.encoders import DataclassJSONEncoder


@attr.s(auto_attribs=True, frozen=True)
class GenericFieldMapping:
    type: ShotgridType
    mapping_table: Dict[str, str]

    def value(self, sg_field: ShotgridField):
        return self.mapping_table.get(sg_field.value)


@attr.s(auto_attribs=True, frozen=True)
class TaskFieldsMapping(GenericFieldMapping):
    type: ShotgridType = field(init=False, default=ShotgridType.TASK)

    @staticmethod
    def from_dict(dic: Dict[str, str]) -> "TaskFieldsMapping":
        return TaskFieldsMapping(
            {
                ShotgridField.CONTENT.value: ShotgridField.CONTENT.value,
                ShotgridField.ID.value: ShotgridField.ID.value,
                ShotgridField.STEP.value: ShotgridField.STEP.value,
                ShotgridField.ENTITY.value: ShotgridField.ENTITY.value,
                **dic,
            }
        )


@attr.s(auto_attribs=True, frozen=True)
class ShotFieldsMapping(GenericFieldMapping):
    type: ShotgridType = field(init=False, default=ShotgridType.SHOT)

    @staticmethod
    def from_dict(dic: Dict[str, str]) -> "ShotFieldsMapping":
        return ShotFieldsMapping(
            {
                ShotgridField.SEQUENCE.value: "sg_sequence",
                ShotgridField.EPISODE.value: "sg_episode",
                ShotgridField.CUT_DURATION.value: "sg_cut_duration",
                ShotgridField.FRAME_RATE.value: "sg_frame_rate",
                ShotgridField.SEQUENCE_EPISODE.value: ".".join(
                    ["sg_sequence", "Sequence", "episode"]
                ),
                ShotgridField.CODE.value: ShotgridField.CODE.value,
                ShotgridField.ID.value: ShotgridField.ID.value,
                **dic,
            }
        )


@attr.s(auto_attribs=True, frozen=True)
class ProjectFieldsMapping(GenericFieldMapping):
    type: ShotgridType = field(init=False, default=ShotgridType.PROJECT)

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "ProjectFieldsMapping":
        return ProjectFieldsMapping(
            {
                ShotgridField.NAME.value: ShotgridField.NAME.value,
                ShotgridField.TYPE.value: ShotgridField.TYPE.value,
                ShotgridField.ID.value: ShotgridField.ID.value,
                **dic,
            }
        )


@attr.s(auto_attribs=True, frozen=True)
class AssetFieldsMapping(GenericFieldMapping):
    type: ShotgridType = field(init=False, default=ShotgridType.ASSET)

    @staticmethod
    def from_dict(dic: Dict[str, str]) -> "AssetFieldsMapping":
        return AssetFieldsMapping(
            {
                ShotgridField.ID.value: ShotgridField.ID.value,
                ShotgridField.TYPE.value: ShotgridField.TYPE.value,
                ShotgridField.TASKS.value: ShotgridField.TASKS.value,
                ShotgridField.ASSET_TYPE.value: "sg_asset_type",
                ShotgridField.CODE.value: ShotgridField.CODE.value,
                **dic,
            }
        )


@attr.s(auto_attribs=True, frozen=True)
class FieldsMapping:
    project: ProjectFieldsMapping
    asset: AssetFieldsMapping
    shot: ShotFieldsMapping
    task: TaskFieldsMapping

    @staticmethod
    def from_dict(dic: Dict[str, Dict[str, str]]) -> "FieldsMapping":
        return FieldsMapping(
            project=ProjectFieldsMapping.from_dict(
                dic.get(ShotgridType.PROJECT.value.lower(), {})
            ),
            asset=AssetFieldsMapping.from_dict(
                dic.get(ShotgridType.ASSET.value.lower(), {})
            ),
            shot=ShotFieldsMapping.from_dict(
                dic.get(ShotgridType.SHOT.value.lower(), {})
            ),
            task=TaskFieldsMapping.from_dict(
                dic.get(ShotgridType.TASK.value.lower(), {})
            ),
        )


@attr.s(auto_attribs=True, frozen=True)
class GenericSubtype:
    id: int
    name: str
    type: str

    def to_json(self) -> str:
        return json.dumps(self, cls=DataclassJSONEncoder)

    def to_dict(self) -> Dict[str, Any]:
        return attr.asdict(self)


@attr.s(auto_attribs=True, frozen=True)
class ShotgridUser(GenericSubtype):
    pass


@attr.s(auto_attribs=True, frozen=True)
class ShotgridProject(GenericSubtype):
    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "ShotgridProject":
        return ShotgridProject(
            id=dic["id"],
            name=dic["name"],
            type=dic["type"],
        )


@attr.s(auto_attribs=True, frozen=True)
class ShotgridEntity(GenericSubtype):
    pass
