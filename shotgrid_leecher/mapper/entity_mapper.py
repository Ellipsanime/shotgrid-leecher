from typing import Dict, Any

from toolz import curry, get_in

from shotgrid_leecher.record.enums import ShotgridField
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridTask,
    ShotgridTaskEntity,
    ShotgridTaskStep,
    ShotgridShot,
)
from shotgrid_leecher.record.shotgrid_subtypes import (
    TaskFieldMapping,
    ShotFieldMapping,
)
from shotgrid_leecher.utils.collections import swap_mapping_keys_values

Map = Dict[str, Any]


@curry
def to_shotgrid_shot(
    shot_mapping: ShotFieldMapping,
    target: Map,
) -> ShotgridShot:
    data = swap_mapping_keys_values(shot_mapping.mapping_table, target)
    shot = ShotgridShot(
        id=data[shot_mapping.ID],
        cut_duration=data[shot_mapping._CUT_DURATION],
        frame_rate=data,
    )


@curry
def to_shotgrid_task(
    task_mapping: TaskFieldMapping,
    target: Map,
) -> ShotgridTask:
    step_field = task_mapping.value(ShotgridField.STEP)
    entity_field = task_mapping.value(ShotgridField.ENTITY)
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
        id=data[task_mapping.value(ShotgridField.ID)],
        content=data[task_mapping.value(ShotgridField.CONTENT)],
        name=data[task_mapping.value(ShotgridField.NAME)],
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
