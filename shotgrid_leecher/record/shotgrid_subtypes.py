import json
from dataclasses import dataclass, asdict, field
from typing import Dict, Any

from dacite import from_dict

from shotgrid_leecher.record.enums import ShotgridType, ShotgridField
from shotgrid_leecher.utils.encoders import DataclassJSONEncoder


@dataclass(frozen=True)
class GenericFieldMapping:
    type: ShotgridType
    mapping_table: Dict[str, str]

    def value(self, sg_field: ShotgridField):
        return self.mapping_table.get(sg_field.value)


@dataclass(frozen=True)
class TaskFieldsMapping(GenericFieldMapping):
    type: ShotgridType = field(init=False, default=ShotgridType.TASK)

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "TaskFieldsMapping":
        return TaskFieldsMapping(
            {
                ShotgridField.CONTENT.value: ShotgridField.CONTENT.value,
                ShotgridField.NAME.value: ShotgridField.NAME.value,
                ShotgridField.ID.value: ShotgridField.ID.value,
                ShotgridField.STEP.value: ShotgridField.STEP.value,
                ShotgridField.ENTITY.value: ShotgridField.ENTITY.value,
                **dic.get(ShotgridType.TASK.value.lower(), dict()),
            }
        )


@dataclass(frozen=True)
class ShotFieldsMapping(GenericFieldMapping):
    type: ShotgridType = field(init=False, default=ShotgridType.SHOT)

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "ShotFieldsMapping":
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
                **dic.get(ShotgridType.SHOT.value.lower(), dict()),
            }
        )


@dataclass(frozen=True)
class ProjectFieldsMapping(GenericFieldMapping):
    type: ShotgridType = field(init=False, default=ShotgridType.PROJECT)

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "ProjectFieldsMapping":
        return ProjectFieldsMapping(
            {
                ShotgridField.NAME.value: ShotgridField.NAME.value,
                **dic.get(ShotgridType.PROJECT.value.lower(), dict()),
            }
        )


@dataclass(frozen=True)
class AssetFieldsMapping(GenericFieldMapping):
    type: ShotgridType = field(init=False, default=ShotgridType.ASSET)

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "AssetFieldsMapping":
        return AssetFieldsMapping(
            {
                ShotgridField.ID.value: ShotgridField.ID.value,
                ShotgridField.TYPE.value: ShotgridField.TYPE.value,
                ShotgridField.TASKS.value: ShotgridField.TASKS.value,
                ShotgridField.ASSET_TYPE.value: "sg_asset_type",
                ShotgridField.CODE.value: ShotgridField.CODE.value,
                **dic.get(ShotgridType.ASSET.value.lower(), dict()),
            }
        )


@dataclass(frozen=True)
class FieldsMapping:
    project_mapping: ProjectFieldsMapping
    asset_mapping: AssetFieldsMapping
    shot_mapping: ShotFieldsMapping
    task_mapping: TaskFieldsMapping

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "FieldsMapping":
        return FieldsMapping(
            project_mapping=ProjectFieldsMapping.from_dict(
                dic.get(ShotgridType.PROJECT.value.lower(), {})
            ),
            asset_mapping=AssetFieldsMapping.from_dict(
                dic.get(ShotgridType.ASSET.value.lower(), {})
            ),
            shot_mapping=ShotFieldsMapping.from_dict(
                dic.get(ShotgridType.SHOT.value.lower(), {})
            ),
            task_mapping=TaskFieldsMapping.from_dict(
                dic.get(ShotgridType.TASK.value.lower(), {})
            ),
        )


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
