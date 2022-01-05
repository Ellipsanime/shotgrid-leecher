from itertools import chain
from typing import Dict, Any, List, Optional, Iterator, cast, Union

import attr
from bson import ObjectId
from toolz import pipe, curry
from toolz.curried import (
    filter as where,
    map as select,
    reduce,
)

from shotgrid_leecher.record.avalon_structures import AvalonProject
from shotgrid_leecher.record.enums import ShotgridType, AvalonType
from shotgrid_leecher.record.intermediate_structures import (
    IntermediateRow,
    IntermediateProject,
    IntermediateTask,
    IntermediateShot,
    IntermediateAsset,
)
from shotgrid_leecher.utils.functional import try_or
from shotgrid_leecher.utils.logger import get_logger

_LOG = get_logger(__name__.split(".")[-1])

Map = Dict[str, Any]

_CONF_MAPPING = {
    "steps": "tasks",
}


def entity_to_project(
    project: AvalonProject, intermediate_rows: List[IntermediateRow]
) -> Optional[IntermediateProject]:
    if not project:
        return None

    shotgrid_project = cast(
        IntermediateProject,
        [x for x in intermediate_rows if x.type == ShotgridType.PROJECT][-1],
    )

    return attr.evolve(shotgrid_project, object_id=project.object_id())


def shotgrid_to_avalon(
    intermediate_rows: List[IntermediateRow],
) -> List[Map]:
    """
    Utility function to map hierarchy shotgrid data to MongoDB avalon format.

    Note:
        intermediate_rows should be ordered from top to bottom
        according to the shotgrid hierarchy.

    Args:
        intermediate_rows list(IntermediateRow):
        list of rows to format to avalon format.

    Returns list(dict(str, any)): List of formatted rows with  mongodb rows.

    """
    if not intermediate_rows:
        return []
    project_rows = [
        cast(IntermediateProject, x)
        for x in intermediate_rows
        if x.type == ShotgridType.PROJECT
    ]
    _check_project_row(project_rows)
    project = _project_row(project_rows[0])
    tasks_hash = _find_tasks(intermediate_rows)
    _check_task_types(project, tasks_hash)
    avalon_rows = _asset_rows(intermediate_rows, project, tasks_hash)

    return [project] + list(avalon_rows)


def _check_project_row(project_rows: List[IntermediateProject]):
    if len(project_rows) > 1:
        msg = (
            "Could not parse shotgrid data to avalon,"
            + "multiple project entities found !"
        )
        _LOG.error(msg)
        raise ValueError(msg)
    if len(project_rows) < 1:
        msg = (
            "Could not parse shotgrid data to avalon,"
            + " no project entity found !"
        )
        _LOG.error(msg)
        raise ValueError(msg)


def _check_task_types(
    project: Map, task_rows: Dict[ObjectId, List[IntermediateTask]]
):
    project_tasks = set(project["config"]["tasks"])
    tasks_difference = {
        *{x.task_type for x in chain(*list(task_rows.values()))},
        *project_tasks,
    }.difference(project_tasks)
    if tasks_difference:
        raise RuntimeError(f"Task types {tasks_difference} are unknown")


def _reduce_found_tasks(
    acc: Dict[ObjectId, List[IntermediateTask]], x: IntermediateTask
) -> Dict[ObjectId, List[IntermediateTask]]:
    return {
        **acc,
        x.parent_id: acc.get(x.parent_id, []) + [x],
    }


def _find_tasks(
    rows: List[IntermediateRow],
) -> Dict[ObjectId, List[IntermediateTask]]:
    tasks_hash = pipe(
        rows,
        where(lambda x: x.type == ShotgridType.TASK),
        select(curry(cast)(IntermediateTask)),
        lambda x: reduce(_reduce_found_tasks, x, dict()),
    )
    return tasks_hash


def _get_parent(row: IntermediateRow) -> str:
    if not row.parent:
        raise ValueError(f"No parent on the middle node {row}")
    return row.parent.split(",")[-2]


def _asset_rows(
    intermediate_rows: List[IntermediateRow],
    project: Map,
    tasks_hash: Dict[ObjectId, List[IntermediateTask]],
) -> Iterator[Map]:

    aka_asset_types = ShotgridType.middle_types()
    asset_rows = [x for x in intermediate_rows if x.type in aka_asset_types]

    for row in asset_rows:
        tasks = tasks_hash.get(row.object_id, [])
        yield _create_avalon_asset_row(row, project, tasks)


def _project_data(project: IntermediateProject) -> Map:
    return {
        "code": project.code,
        "library_project": False,
        "parent": [],
        "visualParent": None,
        "tasks": {},
        **project.params.to_avalonish_dict(),
    }


def _to_project_config(project: IntermediateProject) -> Map:
    return {
        _CONF_MAPPING.get(k, k): v for k, v in project.config.to_dict().items()
    }


def _try_fortify_object_id(object_id: Any) -> ObjectId:
    return try_or(
        lambda: object_id
        if type(object_id) == ObjectId
        else ObjectId(str(object_id)),
        object_id,
    )


def _project_row(project: IntermediateProject) -> Map:
    return {
        "_id": _try_fortify_object_id(project.object_id),
        "type": AvalonType.PROJECT.value,
        "name": project.id,
        "data": _project_data(project),
        "schema": "openpype:project-3.0",
        "config": _to_project_config(project),
    }


def _inputs(row: IntermediateRow) -> Map:
    if row.type not in {ShotgridType.SHOT, ShotgridType.ASSET}:
        return {}
    row = cast(Union[IntermediateShot, IntermediateAsset], row)
    linked_assets = [x for x in row.linked_entities if x.object_id]
    if not linked_assets:
        return {}
    return {
        "inputLinks": [
            {
                "id": _try_fortify_object_id(x.object_id),
                "linkedBy": "shotgrid",
                "type": "breakdown",
                "quantity": x.quantity,
            }
            for x in linked_assets
        ]
    }


def _create_avalon_asset_row(
    intermediate_row: IntermediateRow,
    project: Dict[str, Any],
    tasks: List[IntermediateTask],
) -> Map:
    first_level_citizen = str(project["_id"]) != str(
        intermediate_row.parent_id
    )
    tasks_hash = _create_task_rows(tasks)
    data = _create_data_row(first_level_citizen, intermediate_row, tasks_hash)
    return {
        "_id": _try_fortify_object_id(intermediate_row.object_id),
        "type": AvalonType.ASSET.value,
        "name": intermediate_row.id,
        "data": data,
        "schema": "openpype:asset-3.0",
        "parent": project["_id"],
    }


def _create_data_row(
    first_level_citizen: bool,
    intermediate_row: IntermediateRow,
    tasks: Map,
) -> Map:
    return {
        **intermediate_row.params.to_avalonish_dict(),
        **_inputs(intermediate_row),
        "tasks": tasks,
        "parents": intermediate_row.parent.split(",")[2:-1],
        "visualParent": (
            intermediate_row.parent_id if first_level_citizen else None
        ),
    }


def _create_task_rows(tasks: List[IntermediateTask]) -> Map:
    return reduce(
        lambda acc, x: {
            **acc,
            x.id
            if acc.get(x.id.split("_")[0])
            else x.id.split("_")[0]: {"type": x.task_type},
        },
        tasks,
        dict(),
    )
