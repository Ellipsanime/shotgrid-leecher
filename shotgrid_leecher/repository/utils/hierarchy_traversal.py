import time
from typing import Set, List, Tuple, Dict, Any

import shotgun_api3 as sg
from retry import retry

from shotgrid_leecher.mapper import hierarchy_mapper as mapper
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridNode,
    ShotgridParentPaths,
)
from shotgrid_leecher.repository.utils.traversal_rules import (
    ENTITY_TRAVERSAL_RULES,
)
from shotgrid_leecher.utils.logger import get_logger


class ShotgridClient:
    client: sg.Shotgun

    def __init__(self, client: sg.Shotgun) -> None:
        super().__init__()
        self.client = client

    @retry(tries=3, backoff=0.7)
    def find_one(
        self, type_: str, filters: List[List[Any]], fields: List[str]
    ) -> Dict[str, Any]:
        return self.client.find_one(type_, filters, fields)

    @retry(tries=3, backoff=1.5)
    def find(
        self, type_: str, filters: List[List[Any]], fields: List[str]
    ) -> List[Dict[str, Any]]:
        return self.client.find(type_, filters, fields)


class ShotgridFindHierarchyTraversal:
    _logger = get_logger(__name__.split(".")[-1])
    project_id: int
    client: ShotgridClient
    rules: Dict[str, Any] = ENTITY_TRAVERSAL_RULES

    def __init__(self, project_id: int, client: ShotgridClient) -> None:
        super().__init__()
        self.client = client
        self.project_id = project_id

    # shotgrid.schema_read()["Asset"].keys()
    # shotgrid.find("Asset", [["project", "is", proj]],
    # -- ["tasks", "code", "sg_asset_type"])
    # shotgrid.find("Shot", [["project", "is", proj],],
    #  -- ["tasks", "sg_cut_duration", "sg_frame_rate", "code"])
    # shotgrid.find("Task", [["project", "is", proj],],
    # -- ["content", "name", "id", "step"])
    def traverse_from_the_top(self) -> List[Dict[str, Any]]:
        project = self.client.find_one(
            "Project", [["id", "is", self.project_id]], ["code"]
        )

        mongo_lines = [
            {"_id": project["code"], "type": "Project", "parent": None}
        ]
        tasks = self._fetch_project_tasks(project)
        mongo_lines = mongo_lines + self._fetch_project_assets(project, tasks)
        # mongo_lines = mongo_lines + self._fetch_project_shots(project, tasks)

        return mongo_lines

    def _fetch_project_tasks(self, project: Dict):

        # TODO: Fields should be configurable
        tasks = self.client.find(
            "Task",
            [
                ["project", "is", project],
            ],
            ["content", "name", "id", "step"],
        )
        return {task["id"]: task for task in tasks}

    def _fetch_project_assets(self, project: Dict, tasks: Dict):

        # TODO: Fields should be configurable
        assets = self.client.find(
            "Asset",
            [["project", "is", project]],
            ["tasks", "code", "sg_asset_type"],
        )
        mongo_assets = [
            {"_id": "Asset", "type": "Group", "parent": f",{project['code']},"}
        ]

        step = []
        for asset in assets:

            if asset["sg_asset_type"] not in step:
                mongo_assets.append(self._get_group_line(asset, project))
                step.append(asset["sg_asset_type"])

            parent_path = f",{project['code']},Asset,{asset['sg_asset_type']},"
            mongo_assets.append(self._get_asset_line(asset, parent_path))

            for task in asset["tasks"]:
                parent_task_path = f"{parent_path}{asset['code']},"
                task = tasks[task["id"]]
                mongo_assets.append(
                    self._get_task_line(parent_task_path, task)
                )

        return mongo_assets

    def _get_task_line(self, parent_task_path, task):
        return {
            "_id": f"{task['content']}_{task['id']}",
            "src_id": task["id"],
            "type": "Task",
            "parent": parent_task_path,
            "task_type": task["step"]["name"],
        }

    def _get_asset_line(self, asset, parent_path):
        return {
            "_id": asset["code"],
            "src_id": asset["id"],
            "type": "Asset",
            "parent": parent_path,
        }

    def _get_group_line(self, asset, project):
        return {
            "_id": asset["sg_asset_type"],
            "type": "Group",
            "parent": f",{project['code']},Asset,",
        }

    def _fetch_project_shots(self, project, tasks):
        pass


class ShotgridNavHierarchyTraversal:
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
        return node.system_path in self.visited_paths

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
        raw_data = self._fetch_from_hierarchy(child.system_path)
        children = self._get_children(raw_data)
        self.visited_paths = {*self.visited_paths, child.system_path}
        current_paths = ShotgridParentPaths(
            raw_data["parent_path"], f"{parent_paths.short_path}/{child.label}"
        )
        return child.copy_with_children(
            self._traverse_sub_levels(children, current_paths),
        ).copy_with_parent_paths(parent_paths)
