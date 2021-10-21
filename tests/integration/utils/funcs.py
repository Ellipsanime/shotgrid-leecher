from typing import Any, List, Union, Dict

from toolz import curry

from shotgrid_leecher.record.enums import ShotgridType

Map = Dict[str, Any]


@curry
def sg_query(
    data: Any,
    type_: str,
    filters: List[List[Any]],
    fields: List[str],
) -> Union[List[Map], Map]:
    if type_ == ShotgridType.PROJECT.value:
        return data.SHOTGRID_DATA_PROJECT[0]
    if type_ == ShotgridType.ASSET.value:
        return data.SHOTGRID_DATA_ASSETS
    if type_ == ShotgridType.SHOT.value:
        return data.SHOTGRID_DATA_SHOTS
    if type_ == ShotgridType.TASK.value:
        return data.SHOTGRID_DATA_TASKS
    raise RuntimeError(f"Unknown type {type_}")
