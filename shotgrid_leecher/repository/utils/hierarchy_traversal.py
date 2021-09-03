from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Iterator

import dacite
from toolz import pipe, get_in
from toolz.curried import (
    groupby,
)

from shotgrid_leecher.repository.utils.traversal_rules import (
    ENTITY_TRAVERSAL_RULES,
)
from shotgrid_leecher.utils.connectivity import ShotgridClient
from shotgrid_leecher.utils.logger import get_logger

Map = Dict[str, Any]


@dataclass(frozen=True)
class RawEntity:
    type: str
    id: int
    name: str


@dataclass(frozen=True)
class RawStep:
    name: str


@dataclass(frozen=True)
class RawTask:
    type: str
    id: int
    content: str
    step: Optional[RawStep]
    entity: RawEntity

    @staticmethod
    def from_dict(dic: Map) -> "RawTask":
        return dacite.from_dict(data_class=RawTask, data=dic)


@dataclass(frozen=True)
class RawAsset:
    id: int
    sg_asset_type: str
    type: str
    code: str

    @staticmethod
    def from_dict(dic: Map) -> "RawAsset":
        return dacite.from_dict(data_class=RawAsset, data=dic)


@dataclass(frozen=True)
class RawShot:
    id: int

    @staticmethod
    def from_dict(dic: Map) -> "RawShot":
        return dacite.from_dict(data_class=RawShot, data=dic)


class ShotgridFindHierarchyTraversal:
    _logger = get_logger(__name__.split(".")[-1])
    project_id: int
    client: ShotgridClient
    rules: Map = ENTITY_TRAVERSAL_RULES

    def __init__(self, project_id: int, client: ShotgridClient) -> None:
        super().__init__()
        self.client = client
        self.project_id = project_id

    def traverse_from_the_top(self) -> List[Map]:
        project = self.client.find_one(
            "Project", [["id", "is", self.project_id]], ["code"]
        )
        assets = list(self._fetch_project_assets(project))
        shots = list(self._fetch_project_shots(project))
        rows_dict = {x["src_id"]: x for x in assets + shots if "src_id" in x}
        tasks = list(self._fetch_project_tasks(project, rows_dict))

        return [
            {
                "_id": project["code"],
                "src_id": self.project_id,
                "type": "Project",
                "parent": None,
            },
            *assets,
            *shots,
            *tasks,
        ]

    def _fetch_project_tasks(
        self, project: Map, rows: Dict[str, Map]
    ) -> Iterator[Map]:

        # TODO: Fields should be configurable
        tasks = self.client.find(
            "Task",
            [["project", "is", project], ["entity", "is_not", None]],
            ["content", "name", "id", "step", "entity"],
        )

        for task in tasks:

            entity_row = rows[task["entity"]["id"]]
            parent_path = f"{entity_row['parent']}{entity_row['_id']},"
            yield self._get_task_line(parent_path, task)

    def _fetch_project_shots(self, project: Map) -> Iterator[Map]:

        # TODO: Fields should be configurable
        shots = self.client.find(
            "Shot",
            [["project", "is", project]],
            [
                "sg_sequence",
                "sg_episode",
                "sg_cut_duration",
                "sg_frame_rate",
                "sg_sequence.Sequence.episode",
                "code",
            ],
        )

        if shots:
            yield {
                "_id": "Shot",
                "type": "Group",
                "parent": f",{project['code']},",
            }

        def add_episode(episode, episodes):
            if shot["sg_episode"] not in episodes:
                episodes.append(episode)
                return self._get_episode_shot_group_line(episode, project)

        sequences = []
        episodes: List[Any] = []

        # yield from self.group_all(project, shots)

        for shot in shots:

            parent_shot_path = f",{project['code']},Shot,"

            if shot["sg_episode"]:
                parent_shot_path = (
                    f"{parent_shot_path}{shot['sg_episode']['name']},"
                )
                yield add_episode(shot["sg_episode"], episodes)

            if shot["sg_sequence"] and shot["sg_sequence"] not in sequences:
                parent_shot_path = (
                    f"{parent_shot_path}{shot['sg_sequence']['name']},"
                )
                parent_seq_path = f",{project['code']},Shot,"

                if shot["sg_episode"]:
                    parent_seq_path = (
                        f"{parent_seq_path}{shot['sg_episode']['name']},"
                    )

                elif shot["sg_sequence.Sequence.episode"]:
                    yield add_episode(
                        shot["sg_sequence.Sequence.episode"], episodes
                    )
                    parent_seq_path = (
                        parent_seq_path
                        + shot["sg_sequence.Sequence.episode"]["name"]
                        + ","
                    )

                sequences.append(shot["sg_sequence"])
                yield self._get_sequence_shot_group_line(shot, parent_seq_path)

            yield self._get_shot_line(shot, parent_shot_path)

    def group_all(self, project, shots):
        sequence_groups = pipe(
            shots,
            groupby(
                lambda x: get_in("sg_sequence.name".split("."), x, "None")
            ),
        )
        episode_groups = pipe(
            shots,
            groupby(lambda x: get_in("sg_episode.name".split("."), x, "None")),
        )
        orphans = episode_groups["None"] + sequence_groups["None"]
        for orphan in orphans:
            parent_shot_path = f",{project['code']},Shot,"
            if not orphan["sg_episode"] and not orphan["sg_sequence"]:
                yield self._get_shot_line(orphan, parent_shot_path)
            if not orphan["sg_episode"] and orphan["sg_sequence"]:
                pass
            if orphan["sg_episode"] and not orphan["sg_sequence"]:
                yield self._get_shot_line(
                    orphan,
                    f"{parent_shot_path}{orphan['sg_episode']['name']},",
                )
        # for episode_orphan

    def _fetch_project_assets(self, project: Map) -> Iterator[Map]:
        # TODO: Fields should be configurable
        assets = self.client.find(
            "Asset",
            [["project", "is", project]],
            ["code", "sg_asset_type"],
        )

        if assets:
            yield {
                "_id": "Asset",
                "type": "Group",
                "parent": f",{project['code']},",
            }

        step = []
        for asset in assets:

            if asset["sg_asset_type"] not in step:
                yield self._get_asset_group_line(asset, project)
                step.append(asset["sg_asset_type"])

            parent_path = f",{project['code']},Asset,{asset['sg_asset_type']},"
            yield self._get_asset_line(asset, parent_path)

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

    def _get_shot_line(self, shot, parent_path):
        return {
            "_id": shot["code"],
            "src_id": shot["id"],
            "type": "Shot",
            "parent": parent_path,
        }

    def _get_asset_group_line(self, asset, project):
        return {
            "_id": asset["sg_asset_type"],
            "type": "Group",
            "parent": f",{project['code']},Asset,",
        }

    def _get_episode_shot_group_line(self, episode, project):
        return {
            "_id": episode["name"],
            "type": "Episode",
            "src_id": episode["id"],
            "parent": f",{project['code']},Shot,",
        }

    def _get_sequence_shot_group_line(self, shot, parent_path):
        return {
            "_id": shot["sg_sequence"]["name"],
            "type": "Sequence",
            "src_id": shot["sg_sequence"]["id"],
            "parent": parent_path,
        }
