from typing import Dict, Any, Optional, Callable, TypeVar

from toolz import curry, get_in

from shotgrid_leecher.record.enums import ShotgridField, ShotgridTypes
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridTask,
    ShotgridTaskEntity,
    ShotgridTaskStep,
    ShotgridShot,
    ShotgridShotSequence,
    ShotgridShotEpisode,
)
from shotgrid_leecher.record.shotgrid_subtypes import (
    TaskFieldMapping,
    ShotFieldMapping,
)
from shotgrid_leecher.utils.collections import swap_mapping_keys_values

Map = Dict[str, Any]
TOut = TypeVar("TOut")


@curry
def to_shotgrid_shot(
    shot_mapping: ShotFieldMapping,
    target: Map,
) -> ShotgridShot:
    data = swap_mapping_keys_values(shot_mapping.mapping_table, target)
    sequence: ShotgridShotSequence = _sub_entity(
        ShotgridField.SEQUENCE.value,
        ShotgridShotSequence,
        data,
    )
    episode: ShotgridShotEpisode = _sub_entity(
        ShotgridField.EPISODE.value,
        ShotgridShotEpisode,
        data,
    )
    sequence_episode: ShotgridShotEpisode = _sub_entity(
        ShotgridField.SEQUENCE_EPISODE.value,
        ShotgridShotEpisode,
        data,
    )
    return ShotgridShot(
        id=data[ShotgridField.ID.value],
        cut_duration=data.get(ShotgridField.CUT_DURATION.value),
        frame_rate=data.get(ShotgridField.FRAME_RATE.value),
        code=data[ShotgridField.CODE.value],
        type=data.get(ShotgridField.TYPE.value, ShotgridTypes.SHOT.value),
        sequence=sequence,
        episode=episode,
        sequence_episode=sequence_episode,
    )


@curry
def to_shotgrid_task(
    task_mapping: TaskFieldMapping,
    target: Map,
) -> ShotgridTask:
    step_field = ShotgridField.STEP.value
    entity_field = ShotgridField.ENTITY.value
    data = swap_mapping_keys_values(task_mapping.mapping_table, target)
    entity_id = get_in(
        [entity_field, ShotgridField.ID.value],
        data,
    )
    entity_name = get_in(
        [entity_field, ShotgridField.NAME.value],
        data,
    )
    entity = ShotgridTaskEntity(
        id=entity_id,
        name=entity_name,
    )
    task = ShotgridTask(
        id=data[ShotgridField.ID.value],
        content=data[ShotgridField.CONTENT.value],
        name=data[ShotgridField.NAME.value],
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


def _sub_entity(
    key_field: str,
    ctor: Callable[[int, str, str], TOut],
    data: Map,
) -> Optional[TOut]:
    if not data.get(key_field):
        return None
    id_ = get_in(
        [key_field, ShotgridField.ID.value],
        data,
    )
    name = get_in(
        [key_field, ShotgridField.NAME.value],
        data,
    )
    type_ = get_in(
        [key_field, ShotgridField.TYPE.value],
        data,
    )
    return ctor(id_, name, type_)
