from typing import Dict, Any, List, Optional, Iterator, Tuple

from shotgrid_leecher.utils.logger import get_logger

_LOG = get_logger(__name__.split(".")[-1])

Map = Dict[str, Any]


# def _dict_to_ref(dic: Dict[str, Any]) -> ShotgridRef:
#     if dic.get("kind") == ShotgridRefType.EMPTY.value.lower():
#         return ShotgridRef(ShotgridRefType.EMPTY, None)
#     if dic.get("kind") == ShotgridRefType.LIST.value.lower():
#         return ShotgridRef(ShotgridRefType.LIST, None)
#     try:
#         val: Union[Dict, Any] = dic.get("value", "")
#         if type(val) != dict:
#             type_ = ShotgridRefType[val.strip().upper()]
#             return ShotgridRef(type_, None)
#         type_ = ShotgridRefType[val.get("type").strip().upper()]
#         id_ = int(val.get("id"))
#         return ShotgridRef(type_, id_)
#
#     except KeyError as error:
#         _LOG.warning(error)
#         return ShotgridRef(ShotgridRefType.UNKNOWN, None)
#
#
# def dict_to_shotgrid_node(dic: Dict[str, Any]) -> ShotgridNode:
#     ref = _dict_to_ref(dic.get("ref"))
#     return ShotgridNode(dic.get("label"), dic.get("path"), ref, [])


def shotgrid_to_avalon(intermediate_rows: List[Map]) -> Dict[str, Map]:
    """
    Utilitary function to map intermediate shotgrid data to MongoDB avalon format.

    Note:
        intermediate_rows should be ordered from top to bottom
        according to the shotgrid hierarchy.

    Args:
        intermediate_rows list(dict(str, any)): list of rows to format to avalon format.

    Returns dict(str, dict(str, any)): Map of formatted rows with unique name as key
                                       and mongodb row as value.

    """
    if not intermediate_rows:
        return {}

    project_rows = [x for x in intermediate_rows if x["type"] == "Project"]
    if len(project_rows) > 1:
        msg = (
            "Could not parse shotgrid data to avalon,"
            + "multiple project entities found !"
        )
        _LOG.error(msg)
        raise ValueError(msg)

    if len(project_rows) < 1:
        msg = "Could not parse shotgrid data to avalon, no project entity found !"
        _LOG.error(msg)
        raise ValueError(msg)

    project = _create_avalon_project_row(project_rows[0])

    avalon_rows_dict = dict(
        list(_create_avalon_entity_rows(intermediate_rows, project))
    )
    avalon_rows_dict = {
        project_rows[0]["_id"]: project,
        **avalon_rows_dict,
    }

    task_rows = [x for x in intermediate_rows if x["type"] == "Task"]
    for task_row in task_rows:

        parent = _get_parent(task_row)
        if parent:
            # Add task to the parent entity data
            avalon_rows_dict[parent]["data"]["tasks"][task_row["_id"]] = {
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
    intermediate_rows: List[Map], project: Map
) -> Iterator[Tuple[str, Map]]:

    entity_types = ["Group", "Asset", "Shot", "Episode", "Sequence"]
    entity_rows = [x for x in intermediate_rows if x["type"] in entity_types]

    for intermediate_row in entity_rows:
        parent = _get_parent(intermediate_row)

        visual_parent = None
        if parent != project["name"]:
            visual_parent = parent

        yield (
            intermediate_row["_id"],
            _create_avalon_asset_row(
                intermediate_row, project["name"], visual_parent
            ),
        )


def _default_avalon_data() -> Map:
    return {
        "clipIn": 1,
        "clipOut": 1,
        "fps": 25.0,
        "frameEnd": 0,
        "frameStart": 0,
        "handleEnd": 0,
        "handleStart": 0,
        "pixelAspect": 0,
        "resolutionHeight": 0,
        "resolutionWidth": 0,
        "tools_env": [],
    }


def _default_avalon_project_data() -> Map:
    data = _default_avalon_data()
    data["code"] = ""
    data["library_project"] = False
    return data


def _default_avalon_asset_data() -> Map:
    data = _default_avalon_data()
    data["parent"] = []
    data["visualParent"] = None
    data["tasks"] = {}
    return data


def _create_avalon_project_row(intermediate_row: Map) -> Map:
    return {
        "_id": intermediate_row.get("oid"),
        "type": "project",
        "name": intermediate_row["_id"],
        "data": _default_avalon_project_data(),
        "schema": "openpype:project-3.0",
        "config": {
            "apps": [],
            "imageio": {},
            "roots": {},
            "tasks": {},
            "templates": {},
        },
    }


def _create_avalon_asset_row(
    intermediate_row: Map, parent: str, visual_parent: Optional[str]
) -> Map:
    data = _default_avalon_asset_data()
    data["visualParent"] = visual_parent
    return {
        "_id": intermediate_row.get("oid"),
        "type": "asset",
        "name": intermediate_row["_id"],
        "data": data,
        "schema": "openpype:project-3.0",
        "parent": parent,
    }
