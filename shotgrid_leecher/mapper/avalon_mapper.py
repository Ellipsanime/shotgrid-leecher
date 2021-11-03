from typing import Dict, Any, List, Optional, Iterator, Tuple

from shotgrid_leecher.record.avalon_structures import AvalonProject
from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.utils.logger import get_logger

_LOG = get_logger(__name__.split(".")[-1])

Map = Dict[str, Any]


def entity_to_project(
    project: AvalonProject, hierarchy_rows: List[Map]
) -> Map:
    shotgrid_project = [
        item
        for item in hierarchy_rows
        if item["type"] == ShotgridType.PROJECT.value
    ][-1]

    if not project or not shotgrid_project:
        return {}
    return {
        "_id": shotgrid_project["_id"],
        "src_id": shotgrid_project["src_id"],
        "object_id": project.object_id(),
        "type": "Project",
        "parent": None,
    }


def shotgrid_to_avalon(hierarchy_rows: List[Map]) -> Dict[str, Map]:
    """
    Utilitary function to map hierarchy shotgrid data to MongoDB avalon format.

    Note:
        hierarchy_rows should be ordered from top to bottom
        according to the shotgrid hierarchy.

    Args:
        hierarchy_rows list(dict(str, any)):
        list of rows to format to avalon format.

    Returns dict(str, dict(str, any)): Map of formatted rows with unique
                                       name as key and mongodb row as value.

    """
    if not hierarchy_rows:
        return {}

    project_rows = [x for x in hierarchy_rows if x["type"] == "Project"]
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

    project = _create_avalon_project_row(project_rows[0])

    avalon_rows_dict = dict(
        list(_create_avalon_entity_rows(hierarchy_rows, project))
    )
    avalon_rows_dict = {
        project_rows[0]["_id"]: project,
        **avalon_rows_dict,
    }

    task_rows = [x for x in hierarchy_rows if x["type"] == "Task"]
    for task_row in task_rows:

        parent = _get_parent(task_row)
        if parent:
            # Add task to the parent entity data
            raw_task_name = task_row["_id"].split("_")[0]
            task_name = (
                task_row["_id"]
                if avalon_rows_dict[parent]["data"]["tasks"].get(raw_task_name)
                else raw_task_name
            )

            avalon_rows_dict[parent]["data"]["tasks"][task_name] = {
                "type": task_row["task_type"]
            }
            # Add task type to the project config if it doesn't exist
            if task_row["task_type"] not in project["config"]["tasks"]:
                project["config"]["tasks"][task_row["task_type"]] = {}

    return avalon_rows_dict


def _get_parent(row: Map) -> Optional[str]:
    if "parent" in row and row["parent"]:
        return row["parent"].split(",")[-2]
    return None


def _create_avalon_entity_rows(
    hierarchy_rows: List[Map], project: Map
) -> Iterator[Tuple[str, Map]]:

    entity_types = ["Group", "Asset", "Shot", "Episode", "Sequence"]
    entity_rows = [x for x in hierarchy_rows if x["type"] in entity_types]

    for hierarchy_row in entity_rows:
        parent = _get_parent(hierarchy_row)

        visual_parent = None
        if parent != project["name"]:
            visual_parent = parent

        yield (
            hierarchy_row["_id"],
            _create_avalon_asset_row(
                hierarchy_row, project["name"], visual_parent
            ),
        )


def _default_avalon_data() -> Map:
    return {
        # "clipIn": 1,
        # "clipOut": 1,
        # "fps": 25.0,
        # "frameEnd": 0,
        # "frameStart": 0,
        # "handleEnd": 0,
        # "handleStart": 0,
        # "pixelAspect": 0,
        # "resolutionHeight": 0,
        # "resolutionWidth": 0,
        "tools_env": [],
        "library_project": False,
    }


def _default_avalon_project_data() -> Map:
    # data = _default_avalon_data()
    # data["code"] = ""
    # data["library_project"] = False
    # return data
    return _default_avalon_data()


def _default_avalon_asset_data() -> Map:
    data = _default_avalon_data()
    data["parent"] = []
    data["visualParent"] = None
    data["tasks"] = {}
    return data


def _create_avalon_project_row(hierarchy_row: Map) -> Map:
    return {
        "_id": hierarchy_row.get("object_id"),
        "type": "project",
        "name": hierarchy_row["_id"],
        "data": _default_avalon_project_data(),
        "schema": "openpype:project-3.0",
        "config": {
            "tasks": {},
        },
    }


def _create_avalon_asset_row(
    hierarchy_row: Map, parent: str, visual_parent: Optional[str]
) -> Map:
    def_ = _default_avalon_asset_data()
    params = hierarchy_row.get("params") or dict()
    data = {
        **def_,
        "parents": hierarchy_row["parent"].split(",")[2:-1],
        "visualParent": visual_parent,
        "clipIn": params.get("clip_in") or def_.get("clipIn", 1),
        "clipOut": params.get("clip_out") or def_.get("clipOut", 1),
        "frameStart": params.get("frame_start") or def_.get("frameStart"),
        "frameEnd": params.get("frame_end") or def_.get("frameEnd"),
    }
    return {
        "_id": hierarchy_row.get("object_id"),
        "type": "asset",
        "name": hierarchy_row["_id"],
        "data": data,
        "schema": "openpype:project-3.0",
        "parent": parent,
    }
