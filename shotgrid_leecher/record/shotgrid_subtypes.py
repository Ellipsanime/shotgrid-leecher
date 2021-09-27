import json
from dataclasses import dataclass, asdict, field
from typing import Dict, Any

from dacite import from_dict

from shotgrid_leecher.record.enums import ShotgridTypes
from shotgrid_leecher.utils.encoders import DataclassJSONEncoder


@dataclass(frozen=True)
class GenericFieldMapping:
    type: ShotgridTypes
    mapping_table: Dict[str, str]


@dataclass(frozen=True)
class TaskFieldMapping(GenericFieldMapping):
    type: ShotgridTypes = field(init=False, default=ShotgridTypes.TASK)

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "TaskFieldMapping":
        return TaskFieldMapping(
            {
                "content": "content",
                "name": "name",
                "id": "id",
                "step": "step",
                "entity": "entity",
                **dic.get(ShotgridTypes.TASK.value.lower(), dict()),
            }
        )


@dataclass(frozen=True)
class ShotFieldMapping(GenericFieldMapping):
    type: ShotgridTypes = field(init=False, default=ShotgridTypes.SHOT)

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "ShotFieldMapping":
        return ShotFieldMapping(
            {
                "sequence": "sg_sequence",
                "episode": "sg_episode",
                "cut_duration": "sg_cut_duration",
                "frame_rate": "sg_frame_rate",
                "sequence.episode": "sg_sequence.Sequence.episode",
                "code": "code",
                **dic.get(ShotgridTypes.SHOT.value.lower(), dict()),
            }
        )


@dataclass(frozen=True)
class ProjectFieldMapping(GenericFieldMapping):
    type: ShotgridTypes = field(init=False, default=ShotgridTypes.PROJECT)

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "ProjectFieldMapping":
        return ProjectFieldMapping(
            {
                "name": "name",
                **dic.get(ShotgridTypes.PROJECT.value.lower(), dict()),
            }
        )


@dataclass(frozen=True)
class AssetFieldMapping(GenericFieldMapping):
    type: ShotgridTypes = field(init=False, default=ShotgridTypes.ASSET)

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "AssetFieldMapping":
        return AssetFieldMapping(
            {
                "asset_type": "sg_asset_type",
                "code": "code",
                **dic.get(ShotgridTypes.ASSET.value.lower(), dict()),
            }
        )


@dataclass(frozen=True)
class FieldsMapping:
    project_mapping: ProjectFieldMapping
    asset_mapping: AssetFieldMapping
    shot_mapping: ShotFieldMapping
    task_mapping: TaskFieldMapping

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "FieldsMapping":
        return FieldsMapping(
            project_mapping=ProjectFieldMapping.from_dict(
                dic.get(ShotgridTypes.PROJECT.value.lower(), {})
            ),
            asset_mapping=AssetFieldMapping.from_dict(
                dic.get(ShotgridTypes.ASSET.value.lower(), {})
            ),
            shot_mapping=ShotFieldMapping.from_dict(
                dic.get(ShotgridTypes.SHOT.value.lower(), {})
            ),
            task_mapping=TaskFieldMapping.from_dict(
                dic.get(ShotgridTypes.TASK.value.lower(), {})
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
