import json
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional

from dacite import from_dict

from shotgrid_leecher.record.enums import ShotgridTypes
from shotgrid_leecher.utils.encoders import DataclassJSONEncoder


@dataclass(frozen=True)
class GenericFieldMapping:
    type: ShotgridTypes
    mapping_table: Dict[str, str]


@dataclass(frozen=True)
class TaskFieldMapping(GenericFieldMapping):
    _ENTITY = "entity"
    _ID = "id"
    _STEP = "step"
    _CONTENT = "content"
    type: ShotgridTypes = field(init=False, default=ShotgridTypes.TASK)

    def entity(self) -> Optional[str]:
        return self.mapping_table.get(self._ENTITY)

    def id(self) -> Optional[str]:
        return self.mapping_table.get(self._ID)

    def step(self) -> Optional[str]:
        return self.mapping_table.get(self._STEP)

    def content(self) -> Optional[str]:
        return self.mapping_table.get(self._CONTENT)

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "TaskFieldMapping":
        return TaskFieldMapping(
            {
                TaskFieldMapping._CONTENT: "content",
                "name": "name",
                TaskFieldMapping._ID: "id",
                TaskFieldMapping._STEP: "step",
                TaskFieldMapping._ENTITY: "entity",
                **dic.get(ShotgridTypes.TASK.value.lower(), dict()),
            }
        )


@dataclass(frozen=True)
class ShotFieldMapping(GenericFieldMapping):
    _SEQUENCE = "sequence"
    _EPISODE = "episode"
    _SEQUENCE_EPISODE = "sequence.episode"
    type: ShotgridTypes = field(init=False, default=ShotgridTypes.SHOT)

    def sequence(self) -> Optional[str]:
        return self.mapping_table.get(self._SEQUENCE)

    def sequence_episode(self) -> Optional[str]:
        return self.mapping_table.get(self._SEQUENCE_EPISODE)

    def episode(self) -> Optional[str]:
        return self.mapping_table.get(self._EPISODE)

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "ShotFieldMapping":
        return ShotFieldMapping(
            {
                ShotFieldMapping._SEQUENCE: "sg_sequence",
                ShotFieldMapping._EPISODE: "sg_episode",
                "cut_duration": "sg_cut_duration",
                "frame_rate": "sg_frame_rate",
                ShotFieldMapping._SEQUENCE_EPISODE: "sg_sequence."
                "Sequence.episode",
                "code": "code",
                "id": "id",
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
    _ASSET_TYPE = "asset_type"
    type: ShotgridTypes = field(init=False, default=ShotgridTypes.ASSET)

    def asset_type(self) -> Optional[str]:
        return self.mapping_table.get(self._ASSET_TYPE)

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "AssetFieldMapping":
        return AssetFieldMapping(
            {
                AssetFieldMapping._ASSET_TYPE: "sg_asset_type",
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
