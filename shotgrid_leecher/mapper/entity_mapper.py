from typing import Dict, Any

from dacite import from_dict
from toolz import curry

from shotgrid_leecher.record.shotgrid_structures import ShotgridTask
from shotgrid_leecher.record.shotgrid_subtypes import TaskFieldMapping
from shotgrid_leecher.utils.collections import swap_mapping_keys_values

Map = Dict[str, Any]


@curry
def to_shotgrid_task(
    task_mapping: TaskFieldMapping,
    target: Map,
) -> ShotgridTask:
    data = swap_mapping_keys_values(task_mapping.mapping_table, target)
    return from_dict(ShotgridTask, data)
