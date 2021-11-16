from typing import Dict, Any, List, Optional, Iterator, Tuple, cast

import attr

from shotgrid_leecher.record.avalon_structures import AvalonProject
from shotgrid_leecher.record.enums import ShotgridType, AvalonType
from shotgrid_leecher.record.intermediate_structures import (
    IntermediateRow,
    IntermediateProject,
    IntermediateTask,
    IntermediateShot,
)
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
) -> Dict[str, Map]:
    """
    Utility function to map hierarchy shotgrid data to MongoDB avalon format.

    Note:
        intermediate_rows should be ordered from top to bottom
        according to the shotgrid hierarchy.

    Args:
        intermediate_rows list(IntermediateRow):
        list of rows to format to avalon format.

    Returns dict(str, dict(str, any)): Map of formatted rows with unique
                                       name as key and mongodb row as value.

    """
    if not intermediate_rows:
        return {}

    project_rows = [
        cast(IntermediateProject, x)
        for x in intermediate_rows
        if x.type == ShotgridType.PROJECT
    ]
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

    project = _project_row(project_rows[0])

    avalon_rows_dict = dict(list(_asset_rows(intermediate_rows, project)))
    avalon_rows_dict = {
        project_rows[0].id: project,
        **avalon_rows_dict,
    }
    task_rows: List[IntermediateTask] = [
        cast(IntermediateTask, x)
        for x in intermediate_rows
        if x.type == ShotgridType.TASK
    ]
    for task_row in task_rows:
        parent = _get_parent(task_row)
        if not parent:
            continue
        raw_task_name = task_row.id.split("_")[0]
        task_name = (
            task_row.id
            if avalon_rows_dict[parent]["data"]["tasks"].get(raw_task_name)
            else raw_task_name
        )
        avalon_rows_dict[parent]["data"]["tasks"][task_name] = {
            "type": task_row.task_type
        }
        if task_row.task_type not in project["config"]["tasks"]:
            raise RuntimeError(f"Task type {task_row.task_type} is unknown")

    return avalon_rows_dict


def _get_parent(row: IntermediateRow) -> str:
    if not row.parent:
        raise ValueError(f"No parent on the middle node {row}")
    return row.parent.split(",")[-2]


def _asset_rows(
    intermediate_rows: List[IntermediateRow], project: Map
) -> Iterator[Tuple[str, Map]]:

    aka_asset_types = ShotgridType.middle_types()
    asset_rows = [x for x in intermediate_rows if x.type in aka_asset_types]

    for intermediate_row in asset_rows:
        parent = _get_parent(intermediate_row)
        visual_parent = parent if parent != project["name"] else None

        yield (
            intermediate_row.id,
            _create_avalon_asset_row(
                intermediate_row, project["name"], visual_parent
            ),
        )


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


def _project_row(project: IntermediateProject) -> Map:
    return {
        "_id": project.object_id,
        "type": AvalonType.PROJECT.value,
        "name": project.id,
        "data": _project_data(project),
        "schema": "openpype:project-3.0",
        "config": _to_project_config(project),
    }


def _inputs(row: IntermediateRow) -> Map:
    if row.type != ShotgridType.SHOT:
        return {}
    shot = cast(IntermediateShot, row)
    linked_assets = [x for x in shot.linked_assets if x.object_id]
    if not linked_assets:
        return {}
    return {"inputs": [x.object_id for x in linked_assets]}


def _create_avalon_asset_row(
    intermediate_row: IntermediateRow,
    parent: str,
    visual_parent: Optional[str],
) -> Map:
    data = {
        **intermediate_row.params.to_avalonish_dict(),
        **_inputs(intermediate_row),
        "tasks": dict(),
        "parents": intermediate_row.parent.split(",")[2:-1],
        "visualParent": visual_parent,
    }
    return {
        "_id": intermediate_row.object_id,
        "type": AvalonType.ASSET.value,
        "name": intermediate_row.id,
        "data": data,
        "schema": "openpype:project-3.0",  # TODO check it
        "parent": parent,
    }
