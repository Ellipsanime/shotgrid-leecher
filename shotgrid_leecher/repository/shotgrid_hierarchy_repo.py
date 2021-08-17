from typing import List, Dict, Any

import shotgun_api3 as sg

import shotgrid_leecher.mapper.hierarchy_mapper as mapper
import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.shotgrid_structures import ShotgridNode
from shotgrid_leecher.utils.logger import get_logger

_LOG = get_logger(__name__.split(".")[-1])
_FIRST_LEVEL_FILTER = {"assets", "shots"}


def get_hierarchy_by_project(
    project_id: int,
    client: sg.Shotgun = conn.get_shotgrid_client(),
) -> ShotgridNode:
    raw_data = client.nav_expand(f"/Project/{project_id}")
    children = [
        child
        for child in raw_data.get("children", [])
        if child.get("label", "").lower() in _FIRST_LEVEL_FILTER
    ]
    return mapper.dict_to_shotgrid_node(raw_data).copy_with(
        children=_get_sub_levels(children)
    )


def _fetch_children(raw: Dict[str, Any]) -> ShotgridNode:
    child = mapper.dict_to_shotgrid_node(raw)
    if not raw.get("has_children", False):
        return child
    raw_data = conn.get_shotgrid_client().nav_expand(child.path)
    children = [child for child in raw_data.get("children", [])]
    return child.copy_with(children=_get_sub_levels(children))


def _get_sub_levels(children: List[Dict[str, Any]]) -> List[ShotgridNode]:
    _LOG.debug(f"get sub levels for {len(children)} children")
    return [_fetch_children(x) for x in children]
