from typing import Dict, Any, Optional, Callable, TypeVar, List

import attr
from toolz import curry, get_in

from shotgrid_leecher.record.enums import ShotgridField, ShotgridType
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridTask,
    ShotgridTaskEntity,
    ShotgridTaskStep,
    ShotgridShot,
    ShotgridShotSequence,
    ShotgridShotEpisode,
    ShotgridAsset,
    ShotgridShotParams,
    ShotgridAssetTask,
    ShotgridStep,
    ShotgridEntityToEntityLink,
)
from shotgrid_leecher.record.shotgrid_subtypes import (
    TaskFieldsMapping,
    ShotFieldsMapping,
    AssetFieldsMapping,
    ProjectFieldsMapping,
    ShotgridProject,
    StepFieldsMapping,
    ShotToShotLinkMapping,
    AssetToShotLinkMapping,
    AssetToAssetLinkMapping,
    ShotgridUser,
)
from shotgrid_leecher.utils.collections import swap_mapping_keys_values

Map = Dict[str, Any]
TOut = TypeVar("TOut")


def to_shotgrid_project(
    project_mapping: ProjectFieldsMapping,
    target: Map,
) -> ShotgridProject:
    data = swap_mapping_keys_values(project_mapping.mapping_table, target)
    return ShotgridProject.from_dict(data)


@curry
def to_shotgrid_asset(
    asset_mapping: AssetFieldsMapping,
    task_mapping: TaskFieldsMapping,
    target: Map,
) -> ShotgridAsset:
    data = swap_mapping_keys_values(asset_mapping.mapping_table, target)
    tasks = [
        _to_asset_task(task_mapping, x)
        for x in data.get(ShotgridField.TASKS.value, [])
    ]
    return ShotgridAsset(
        id=data[ShotgridField.ID.value],
        type=data.get(ShotgridField.TYPE.value, ShotgridType.ASSET.value),
        code=data[ShotgridField.CODE.value],
        asset_type=data.get(ShotgridField.ASSET_TYPE.value, None),
        tasks=tasks,
    )


@curry
def to_shot_to_shot_link(
    link_mapping: ShotToShotLinkMapping,
    target: Map,
) -> ShotgridEntityToEntityLink:
    data = swap_mapping_keys_values(link_mapping.mapping_table, target)
    return ShotgridEntityToEntityLink(
        id=data[ShotgridField.ID.value],
        type=ShotgridType.SHOT_TO_SHOT_LINK.value,
        parent_id=data[ShotgridField.LINK_PARENT_SHOT_ID.value],
        child_id=data[ShotgridField.LINK_SHOT_ID.value],
        quantity=data.get(ShotgridField.LINK_QUANTITY.value, 1) or 1,
    )


@curry
def to_asset_to_shot_link(
    link_mapping: AssetToShotLinkMapping,
    target: Map,
) -> ShotgridEntityToEntityLink:
    data = swap_mapping_keys_values(link_mapping.mapping_table, target)
    return ShotgridEntityToEntityLink(
        id=data[ShotgridField.ID.value],
        type=ShotgridType.ASSET_TO_SHOT_LINK.value,
        parent_id=data[ShotgridField.LINK_ASSET_ID.value],
        child_id=data[ShotgridField.LINK_SHOT_ID.value],
        quantity=data.get(ShotgridField.LINK_QUANTITY.value, 1) or 1,
    )


@curry
def to_asset_to_asset_link(
    link_mapping: AssetToAssetLinkMapping,
    target: Map,
) -> ShotgridEntityToEntityLink:
    data = swap_mapping_keys_values(link_mapping.mapping_table, target)
    return ShotgridEntityToEntityLink(
        id=data[ShotgridField.ID.value],
        type=ShotgridType.ASSET_TO_ASSET_LINK.value,
        parent_id=data[ShotgridField.LINK_PARENT_ID.value],
        child_id=data[ShotgridField.LINK_ASSET_ID.value],
        quantity=data.get(ShotgridField.LINK_QUANTITY.value, 1) or 1,
    )


@curry
def to_shotgrid_shot(
    shot_mapping: ShotFieldsMapping,
    target: Map,
) -> ShotgridShot:
    data = swap_mapping_keys_values(shot_mapping.mapping_table, target)
    sequence = _sub_entity(ShotgridField.SEQUENCE, ShotgridShotSequence, data)
    episode = _sub_entity(ShotgridField.EPISODE, ShotgridShotEpisode, data)
    sequence_episode = _sub_entity(
        ShotgridField.SEQUENCE_EPISODE,
        ShotgridShotEpisode,
        data,
    )
    return ShotgridShot(
        id=data[ShotgridField.ID.value],
        params=_to_shot_params(data),
        code=data[ShotgridField.CODE.value],
        type=data.get(ShotgridField.TYPE.value, ShotgridType.SHOT.value),
        sequence=sequence,
        episode=episode,
        sequence_episode=sequence_episode,
    )


@curry
def to_shotgrid_step(
    step_mapping: StepFieldsMapping,
    target: Map,
) -> ShotgridStep:
    data = swap_mapping_keys_values(step_mapping.mapping_table, target)
    return ShotgridStep(
        id=data[ShotgridField.ID.value],
        short_name=data[ShotgridField.SHORT_NAME.value],
        code=data[ShotgridField.CODE.value],
    )


@curry
def to_shotgrid_task(
    task_mapping: TaskFieldsMapping,
    target: Map,
) -> ShotgridTask:
    step_field = ShotgridField.STEP.value
    data = swap_mapping_keys_values(task_mapping.mapping_table, target)
    entity: Optional[ShotgridTaskEntity] = _sub_entity(
        ShotgridField.ENTITY,
        ShotgridTaskEntity,
        data,
    )
    if not entity:
        raise RuntimeError("Entity cannot be null")

    task = ShotgridTask(
        id=data[ShotgridField.ID.value],
        content=data[ShotgridField.CONTENT.value],
        status=data[ShotgridField.TASK_STATUS.value],
        assigned_users=_to_task_users(data),
        entity=entity,
        step=None,
    )
    if not data.get(step_field):
        return task

    return task.copy_with_step(
        ShotgridTaskStep(
            id=get_in([step_field, ShotgridField.ID.value], data),
            name=get_in([step_field, ShotgridField.NAME.value], data),
        )
    )


@curry
def _to_asset_task(
    task_mapping: TaskFieldsMapping,
    target: Map,
) -> ShotgridAssetTask:
    data = swap_mapping_keys_values(
        {
            **task_mapping.mapping_table,
            ShotgridField.NAME.value: ShotgridField.NAME.value,
            ShotgridField.TYPE.value: ShotgridField.TYPE.value,
        },
        target,
    )
    return ShotgridAssetTask(
        id=data[ShotgridField.ID.value],
        name=data[ShotgridField.NAME.value],
        type=data[ShotgridField.TYPE.value],
    )


def _to_task_users(data: Map) -> List[ShotgridUser]:
    ctor = ShotgridUser
    return [
        ctor(**x) for x in data.get(ShotgridField.TASK_ASSIGNEES.value, [])
    ]


def _to_shot_params(data: Map) -> Optional[ShotgridShotParams]:
    keys = set(attr.fields_dict(ShotgridShotParams).keys())
    if not keys.intersection(set(data.keys())):
        return None
    return ShotgridShotParams(**{k: data.get(k) for k in keys})


def _sub_entity(
    field: ShotgridField,
    ctor: Callable[[int, str, str], TOut],
    data: Map,
) -> Optional[TOut]:
    if not data.get(field.value):
        return None
    id_ = get_in(
        [field.value, ShotgridField.ID.value],
        data,
    )
    name = get_in(
        [field.value, ShotgridField.NAME.value],
        data,
    )
    type_ = get_in(
        [field.value, ShotgridField.TYPE.value],
        data,
    )
    return ctor(id_, name, type_)
