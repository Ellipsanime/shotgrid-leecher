from typing import Dict, Any, List

import shotgun_api3 as sg

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.repository.utils.hierarchy_traversal import (
    ShotgridHierarchyTraversal,
)
from shotgrid_leecher.utils.logger import get_logger
from shotgrid_leecher.utils.timer import timed

_LOG = get_logger(__name__.split(".")[-1])


@timed
def get_hierarchy_by_project(
    project_id: int,
    client: sg.Shotgun = conn.get_shotgrid_client(),
) -> List[Dict[str, Any]]:
    traversal = ShotgridHierarchyTraversal(project_id, client)
    result = traversal.traverse_from_the_top()
    _LOG.debug(f"Unique queries length {len(traversal.visited_paths)}")
    return list(result.to_table_iterator())
