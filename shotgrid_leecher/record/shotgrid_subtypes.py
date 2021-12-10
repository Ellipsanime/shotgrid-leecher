import json
from typing import Dict, Any, List, cast

import attr
import cattr

from shotgrid_leecher.record.enums import ShotgridType, ShotgridField
from shotgrid_leecher.utils.encoders import DataclassJSONEncoder


@attr.s(auto_attribs=True, frozen=True)
class GenericFieldsMapping:
    type: ShotgridType
    mapping_table: Dict[str, str]

    def mapping_values(self) -> List[str]:
        return list(self.mapping_table.values())


@attr.s(auto_attribs=True, frozen=True)
class ShotToShotLinkMapping(GenericFieldsMapping):
    type: ShotgridType = ShotgridType.SHOT_TO_SHOT_LINK

    @staticmethod
    def from_dict(dic: Dict[str, str]) -> "ShotToShotLinkMapping":
        def_parent_shot = ShotgridField.LINK_PARENT_SHOT_ID.value
        def_cached_name = ShotgridField.CACHED_DISPLAY_NAME.value
        shot_id = ShotgridField.LINK_SHOT_ID.value
        return ShotToShotLinkMapping(
            {
                ShotgridField.ID.value: ShotgridField.ID.value,
                shot_id: shot_id,
                ShotgridField.LINK_QUANTITY.value: "sg_instance",
                def_parent_shot: def_parent_shot,
                def_cached_name: def_cached_name,
                **dic,
            }
        )


@attr.s(auto_attribs=True, frozen=True)
class AssetToShotLinkMapping(GenericFieldsMapping):
    type: ShotgridType = ShotgridType.ASSET_TO_SHOT_LINK

    @staticmethod
    def from_dict(dic: Dict[str, str]) -> "AssetToShotLinkMapping":
        def_cached_name = ShotgridField.CACHED_DISPLAY_NAME.value
        shot_id = ShotgridField.LINK_SHOT_ID.value
        asset_id = ShotgridField.LINK_ASSET_ID.value
        return AssetToShotLinkMapping(
            {
                ShotgridField.ID.value: ShotgridField.ID.value,
                shot_id: shot_id,
                asset_id: asset_id,
                ShotgridField.LINK_QUANTITY.value: "sg_instance",
                def_cached_name: def_cached_name,
                **dic,
            }
        )


@attr.s(auto_attribs=True, frozen=True)
class AssetToAssetLinkMapping(GenericFieldsMapping):
    type: ShotgridType = ShotgridType.ASSET_TO_ASSET_LINK

    @staticmethod
    def from_dict(dic: Dict[str, str]) -> "AssetToAssetLinkMapping":
        def_cached_name = ShotgridField.CACHED_DISPLAY_NAME.value
        parent_id = ShotgridField.LINK_PARENT_ID.value
        asset_id = ShotgridField.LINK_ASSET_ID.value
        return AssetToAssetLinkMapping(
            {
                ShotgridField.ID.value: ShotgridField.ID.value,
                parent_id: parent_id,
                asset_id: asset_id,
                ShotgridField.LINK_QUANTITY.value: "sg_instance",
                def_cached_name: def_cached_name,
                **dic,
            }
        )


@attr.s(auto_attribs=True, frozen=True)
class StepFieldsMapping(GenericFieldsMapping):
    type: ShotgridType = ShotgridType.STEP

    @staticmethod
    def from_dict(dic: Dict[str, str]) -> "StepFieldsMapping":
        return StepFieldsMapping(
            {
                ShotgridField.ID.value: ShotgridField.ID.value,
                ShotgridField.CODE.value: ShotgridField.CODE.value,
                ShotgridField.SHORT_NAME.value: ShotgridField.SHORT_NAME.value,
                **dic,
            }
        )


@attr.s(auto_attribs=True, frozen=True)
class TaskFieldsMapping(GenericFieldsMapping):
    type: ShotgridType = ShotgridType.TASK

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
class ShotFieldsMapping(GenericFieldsMapping):
    type: ShotgridType = ShotgridType.SHOT

    @staticmethod
    def from_dict(dic: Dict[str, str]) -> "ShotFieldsMapping":
        return ShotFieldsMapping(
            {
                ShotgridField.SEQUENCE.value: "sg_sequence",
                ShotgridField.EPISODE.value: "sg_episode",
                ShotgridField.CUT_DURATION.value: "sg_cut_duration",
                ShotgridField.FRAME_RATE.value: "sg_frame_rate",
                ShotgridField.CUT_IN.value: "sg_cut_in",
                ShotgridField.CUT_OUT.value: "sg_cut_out",
                ShotgridField.HEAD_IN.value: "sg_head_in",
                ShotgridField.HEAD_OUT.value: "sg_head_out",
                ShotgridField.TAIL_IN.value: "sg_tail_in",
                ShotgridField.TAIL_OUT.value: "sg_tail_out",
                ShotgridField.SEQUENCE_EPISODE.value: ".".join(
                    ["sg_sequence", "Sequence", "episode"]
                ),
                ShotgridField.CODE.value: ShotgridField.CODE.value,
                ShotgridField.ASSETS.value: ShotgridField.ASSETS.value,
                ShotgridField.ID.value: ShotgridField.ID.value,
                **dic,
            }
        )


@attr.s(auto_attribs=True, frozen=True)
class ProjectFieldsMapping(GenericFieldsMapping):
    type: ShotgridType = ShotgridType.PROJECT

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "ProjectFieldsMapping":
        return ProjectFieldsMapping(
            {
                ShotgridField.CODE.value: ShotgridField.CODE.value,
                ShotgridField.NAME.value: ShotgridField.NAME.value,
                ShotgridField.TYPE.value: ShotgridField.TYPE.value,
                ShotgridField.ID.value: ShotgridField.ID.value,
                **dic,
            }
        )


@attr.s(auto_attribs=True, frozen=True)
class AssetFieldsMapping(GenericFieldsMapping):
    type: ShotgridType = ShotgridType.ASSET

    @staticmethod
    def from_dict(dic: Dict[str, str]) -> "AssetFieldsMapping":
        return AssetFieldsMapping(
            {
                ShotgridField.ID.value: ShotgridField.ID.value,
                ShotgridField.TYPE.value: ShotgridField.TYPE.value,
                ShotgridField.TASKS.value: ShotgridField.TASKS.value,
                ShotgridField.PARENTS.value: ShotgridField.PARENTS.value,
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
    step: StepFieldsMapping

    @staticmethod
    def from_dict(dic: Dict[str, Dict[str, str]]) -> "FieldsMapping":
        return FieldsMapping(
            project=ProjectFieldsMapping.from_dict(
                dic.get(
                    ShotgridType.PROJECT.value.lower(),
                    cast(Dict[str, str], {}),
                )
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
            step=StepFieldsMapping.from_dict(
                dic.get(ShotgridType.STEP.value.lower(), {})
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
    code: str

    @staticmethod
    def from_dict(raw_dic: Dict[str, Any]) -> "ShotgridProject":
        dic = {"code": "", **raw_dic}
        return cattr.structure(dic, ShotgridProject)


@attr.s(auto_attribs=True, frozen=True)
class ShotgridEntity(GenericSubtype):
    pass
