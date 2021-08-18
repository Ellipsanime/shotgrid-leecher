import time
from typing import List, Dict, Any, Set, Tuple

import shotgun_api3 as sg

import shotgrid_leecher.mapper.hierarchy_mapper as mapper
import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.shotgrid_structures import ShotgridNode
from shotgrid_leecher.utils.logger import get_logger
from shotgrid_leecher.utils.timer import timed

_LOG = get_logger(__name__.split(".")[-1])


class ShotgridHierarchyTraversal:
    _FIRST_LEVEL_FILTER = {"assets", "shots"}
    visited_paths: Set[str] = set()
    project_id: int
    client: sg.Shotgun
    stats: List[Tuple[str, float]] = []

    def __init__(self, project_id: int, client: sg.Shotgun):
        self.project_id = project_id
        self.client = client

    def _fetch_from_hierarchy(self, path: str) -> Dict[str, Any]:
        start = time.time()
        result = self.client.nav_expand(path)
        elapsed = time.time() - start
        self.stats = [*self.stats, (path, elapsed)]
        return result

    def get_traversal_stats(self) -> List[Tuple[str, float]]:
        return self.stats

    def traverse_from_the_top(self) -> ShotgridNode:
        raw_data = self._fetch_from_hierarchy(f"/Project/{self.project_id}")
        children = [
            child
            for child in raw_data.get("children", [])
            if child.get("label", "").lower() in self._FIRST_LEVEL_FILTER
        ]
        self.visited_paths = {*self.visited_paths, raw_data["path"]}
        return mapper.dict_to_shotgrid_node(raw_data).copy_with(
            children=self._traverse_sub_levels(children)
        )

    def _traverse_sub_levels(
        self,
        children: List[Dict[str, Any]],
    ) -> List[ShotgridNode]:
        _LOG.debug(f"get sub levels for {len(children)} children")
        return [
            self._fetch_children(x)
            for x in children
            if x.get("path", "") not in self.visited_paths
        ]

    def _fetch_children(self, raw: Dict[str, Any]) -> ShotgridNode:
        child = mapper.dict_to_shotgrid_node(raw)
        if (
            not raw.get("has_children", False)
            or child.path in self.visited_paths
        ):
            return child
        _LOG.debug(f"get children for {raw.get('path')} path")
        raw_data = self._fetch_from_hierarchy(child.path)
        children = [child for child in raw_data.get("children", [])]
        self.visited_paths = {*self.visited_paths, child.path}
        return child.copy_with(
            children=self._traverse_sub_levels(children),
        )


@timed
def get_hierarchy_by_project(
    project_id: int,
    client: sg.Shotgun = conn.get_shotgrid_client(),
) -> ShotgridNode:
    traversal = ShotgridHierarchyTraversal(project_id, client)
    result = traversal.traverse_from_the_top()
    _LOG.debug(f"Unique queries length {len(traversal.visited_paths)}")
    return result
    # raw_data = client.nav_expand(f"/Project/{project_id}")
    # children = [
    #     child
    #     for child in raw_data.get("children", [])
    #     if child.get("label", "").lower() in _FIRST_LEVEL_FILTER
    # ]
    # return mapper.dict_to_shotgrid_node(raw_data).copy_with(
    #     children=_get_sub_levels(children, paths={raw_data.get("path", "")})
    # )


# def _fetch_children(raw: Dict[str, Any], paths: Set[str]) -> ShotgridNode:
#     child = mapper.dict_to_shotgrid_node(raw)
#     # if not raw.get("has_children", False):
#     if not raw.get("has_children", False) or child.path in paths:
#         return child
#     _LOG.debug(f"get children for {raw.get('path')} path")
#     raw_data = conn.get_shotgrid_client().nav_expand(child.path)
#     children = [child for child in raw_data.get("children", [])]
#     return child.copy_with(
#         children=_get_sub_levels(children, {*paths, child.path}),
#     )
#
#
# def _get_sub_levels(
#     children: List[Dict[str, Any]],
#     paths: Set[str],
# ) -> List[ShotgridNode]:
#     _LOG.debug(f"get sub levels for {len(children)} children")
#     return [
#         _fetch_children(x, paths)
#         for x in children
#         # if x.get("path", "") not in paths
#     ]
