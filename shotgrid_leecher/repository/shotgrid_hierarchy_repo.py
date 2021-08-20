import uuid
from itertools import chain, starmap
from typing import Dict, Any, Tuple, Iterable

import shotgun_api3 as sg
from toolz import curry

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.shotgrid_structures import ShotgridNode
from shotgrid_leecher.repository.utils.hierarchy_traversal import (
    ShotgridHierarchyTraversal,
)
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


def flatten_node(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    dict_ = dictionary
    while True:
        dict_ = dict(
            chain.from_iterable(starmap(_unpack_nested, dict_.items()))
        )
        if not any(type(x) in {list, dict} for x in dict_.values()):
            return dict_


@timed
def get_hierarchy_by_project(
    project_id: int,
    client: sg.Shotgun = conn.get_shotgrid_client(),
) -> ShotgridNode:
    traversal = ShotgridHierarchyTraversal(project_id, client)
    result = traversal.traverse_from_the_top()
    _LOG.debug(f"Unique queries length {len(traversal.visited_paths)}")
    return result
