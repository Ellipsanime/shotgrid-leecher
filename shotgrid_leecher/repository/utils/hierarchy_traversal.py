import time
from typing import Set, List, Tuple, Dict, Any

import shotgun_api3 as sg

from shotgrid_leecher.mapper import hierarchy_mapper as mapper
from shotgrid_leecher.record.shotgrid_structures import ShotgridNode
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
        self._logger.debug(f"get sub levels for {len(children)} children")
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
        self._logger.debug(f"get children for {raw.get('path')} path")
        raw_data = self._fetch_from_hierarchy(child.path)
        children = [child for child in raw_data.get("children", [])]
        self.visited_paths = {*self.visited_paths, child.path}
        return child.copy_with(
            children=self._traverse_sub_levels(children),
        )
