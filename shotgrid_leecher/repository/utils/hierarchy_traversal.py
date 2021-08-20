import time
from typing import Set, List, Tuple, Dict, Any

import shotgun_api3 as sg

from shotgrid_leecher.mapper import hierarchy_mapper as mapper
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridNode,
    ShotgridParentPaths,
)
from shotgrid_leecher.utils.logger import get_logger


class ShotgridHierarchyTraversal:
    _logger = get_logger(__name__.split(".")[-1])
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
        raw = self._fetch_from_hierarchy(f"/Project/{self.project_id}")
        children = [
            child
            for child in raw.get("children", [])
            if child.get("label", "").lower() in self._FIRST_LEVEL_FILTER
        ]
        self.visited_paths = {*self.visited_paths, raw["path"]}
        root = mapper.dict_to_shotgrid_node(raw)
        root_paths = ShotgridParentPaths(raw["parent_path"], f"/{root.label}")
        return root.copy_with_children(
            self._traverse_sub_levels(children, root_paths)
        )

    def _traverse_sub_levels(
        self,
        children: List[Dict[str, Any]],
        parent_paths: ShotgridParentPaths,
    ) -> List[ShotgridNode]:
        self._logger.debug(f"get sub levels for {len(children)} children")
        return [
            self._fetch_children(x, parent_paths)
            for x in children
            if x.get("path", "") not in self.visited_paths
        ]

    def _has_no_children(self, raw: Dict[str, Any]) -> bool:
        return not raw.get("has_children", False)

    def _already_visited(self, node: ShotgridNode) -> bool:
        return node.path in self.visited_paths

    def _get_children(self, raw: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [child for child in raw.get("children", [])]

    def _fetch_children(
        self,
        raw: Dict[str, Any],
        parent_paths: ShotgridParentPaths,
    ) -> ShotgridNode:
        child = mapper.dict_to_shotgrid_node(raw).copy_with_parent_paths(
            parent_paths
        )
        if self._has_no_children(raw) or self._already_visited(child):
            return child
        self._logger.debug(f"get children for {raw.get('path')} path")
        raw_data = self._fetch_from_hierarchy(child.path)
        children = self._get_children(raw_data)
        self.visited_paths = {*self.visited_paths, child.path}
        current_paths = ShotgridParentPaths(
            raw_data["parent_path"], f"{parent_paths.short_path}/{child.label}"
        )
        return child.copy_with_children(
            self._traverse_sub_levels(children, current_paths),
        ).copy_with_parent_paths(parent_paths)
