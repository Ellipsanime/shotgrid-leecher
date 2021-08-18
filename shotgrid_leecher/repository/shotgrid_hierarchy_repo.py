import time
import uuid
from itertools import chain, starmap
from typing import List, Dict, Any, Set, Tuple, Iterable

import shotgun_api3 as sg
from toolz import curry

import shotgrid_leecher.mapper.hierarchy_mapper as mapper
import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.shotgrid_structures import ShotgridNode
from shotgrid_leecher.utils.logger import get_logger
from shotgrid_leecher.utils.timer import timed

_LOG = get_logger(__name__.split(".")[-1])

_EMPTY = f"EMPTY_{str(uuid.uuid4())}"
_SEP = "."
_star_select = curry(starmap)


def _unpack_nested(key: str, value: Any) -> Iterable[Tuple[str, Any]]:
    value_type = type(value)
    if value_type is dict:
        if not value:
            yield key, _EMPTY
        for k, v in value.items():
            yield key + _SEP + k, v
    if value_type is list:
        if not value:
            yield key, _EMPTY
        for i, v in zip(range(len(value)), value):
            yield key + _SEP + str(i), v
    if value_type not in {list, dict}:
        yield key, value


def flatten_dict(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    dict_ = dictionary
    while True:
        dict_ = dict(
            chain.from_iterable(starmap(_unpack_nested, dict_.items()))
        )
        if not any(type(x) in {list, dict} for x in dict_.values()):
            return dict_


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
