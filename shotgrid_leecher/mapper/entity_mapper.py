from typing import Dict, Any

from toolz import curry, get_in

from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridTask,
    ShotgridTaskEntity,
    ShotgridTaskStep,
)
from shotgrid_leecher.record.shotgrid_subtypes import TaskFieldMapping
from shotgrid_leecher.utils.collections import swap_mapping_keys_values

Map = Dict[str, Any]


@curry
def to_shotgrid_task(
    task_mapping: TaskFieldMapping,
    target: Map,
) -> ShotgridTask:
    mapping = task_mapping
    data = swap_mapping_keys_values(mapping.mapping_table, target)
    entity = ShotgridTaskEntity(
        id=get_in([mapping.entity(), "id"], data),
        name=get_in([mapping.entity(), "name"], data),
    )
    task = ShotgridTask(
        id=data[mapping.id()],
        content=data[mapping.content()],
        name=data[mapping.name()],
        entity=entity,
        step=None,
    )
    if not data.get(mapping.step()):
        return task

    return task.copy_with_step(
        ShotgridTaskStep(
            id=get_in([mapping.step(), "id"], data),
            name=get_in([mapping.step(), "name"], data),
        )
    )
