from typing import Dict, Any, List, Iterator

import shotgun_api3 as sg
from toolz import pipe, get_in
from toolz.curried import (
    filter as where,
    map as select,
    unique,
)
from toolz.curried import groupby, get_in as get_in_

from shotgrid_leecher.utils.logger import get_logger
from shotgrid_leecher.utils.timer import timed

_LOG = get_logger(__name__.split(".")[-1])

Map = Dict[str, Any]


def _fetch_project_tasks(
    client: sg.Shotgun,
    project: Map,
    rows: Map,
) -> Iterator[Map]:
    # TODO: Fields should be configurable
    raw_tasks = client.find(
        "Task",
        [
            ["project", "is", project],
            ["entity", "is_not", None],
        ],
        ["content", "name", "id", "step", "entity"],
    )
    asset_tasks = [task for task in raw_tasks if task.get("step")]
    for task in asset_tasks:
        key = task["entity"]["id"]
        entity_row = rows.get(key)
        if not entity_row:
            continue
        parent_path = f"{entity_row['parent']}{entity_row['_id']},"
        yield _get_task_row(task, parent_path)


def _patch_up_shot(shot: Map) -> Map:
    if shot.get("sg_episode") or not shot.get("sg_sequence.Sequence.episode"):
        return shot
    return {
        **shot,
        "sg_episode": shot["sg_sequence.Sequence.episode"],
    }


def _fetch_project_shots(client: sg.Shotgun, project: Map) -> Iterator[Map]:
    # TODO: Fields should be configurable
    raw_shots = client.find(
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

    if raw_shots:
        yield _get_top_shot_row(project)

    shots = pipe(
        raw_shots,
        select(_patch_up_shot),
        list,
    )
    yield from _tackle_orphan_shots(project, shots)
    yield from _tackle_shot_episodes(project, shots)
    yield from _tackle_shot_sequences(project, shots)
    yield from _tackle_full_shots(project, shots)


def _tackle_full_shots(project: Map, shots: Map):
    full_shots = pipe(
        shots,
        where(
            lambda x: get_in("sg_sequence.name".split("."), x)
            and get_in("sg_episode.name".split("."), x)
        ),
        list,
    )
    for shot in full_shots:
        episode = shot["sg_episode"]["name"]
        sequence_ = shot["sg_sequence"]["name"]
        parent_path = f",{project['name']},Shot,{episode},{sequence_},"
        yield _get_shot_row(shot, parent_path)


def _tackle_shot_sequences(project, shots):
    sequence_group = pipe(
        shots,
        where(get_in_("sg_sequence.name".split("."))),
        groupby(get_in_("sg_sequence.name".split("."))),
    )
    for sq, sq_shots in sequence_group.items():
        for shot in unique(sq_shots, get_in_("sg_episode.id".split(".", -1))):
            episode = get_in("sg_episode.name".split("."), shot)
            base_path = f",{project['name']},Shot,"
            parent_path = f"{base_path}{episode}," if episode else base_path
            yield _get_sequence_shot_group_row(shot, parent_path)


def _tackle_shot_episodes(project, shots):
    episode_groups = pipe(
        shots,
        where(get_in_("sg_episode.name".split("."))),
        groupby(get_in_("sg_episode.name".split("."))),
    )
    for ep, ep_shots in episode_groups.items():
        yield _get_episode_shot_group_row(ep_shots[-1]["sg_episode"], project)


def _tackle_orphan_shots(project, shots):
    orphans = pipe(
        shots,
        where(
            lambda x: not get_in("sg_sequence.name".split("."), x)
            or not get_in("sg_episode.name".split("."), x)
        ),
        list,
    )
    for orphan in orphans:
        if not orphan.get("sg_episode") and not orphan.get("sg_sequence"):
            parent_path = f",{project['name']},Shot,"
            yield _get_shot_row(orphan, parent_path)
        if not orphan.get("sg_episode") and orphan.get("sg_sequence"):
            sequence_ = orphan.get("sg_sequence")["name"]
            parent_path = f",{project['name']},Shot,{sequence_},"
            yield _get_shot_row(orphan, parent_path)
        if orphan.get("sg_episode") and not orphan.get("sg_sequence"):
            episode = orphan["sg_episode"]["name"]
            parent_path = f",{project['name']},Shot,{episode},"
            yield _get_shot_row(orphan, parent_path)


def _fetch_project_assets(client: sg.Shotgun, project: Map) -> Iterator[Map]:
    # TODO: Fields should be configurable
    assets = client.find(
        "Asset",
        [["project", "is", project]],
        ["code", "sg_asset_type"],
    )

    if assets:
        yield _get_top_asset_row(project)

    step = []
    for asset in assets:

        if asset["sg_asset_type"] not in step:
            yield _get_asset_group_row(asset, project)
            step.append(asset["sg_asset_type"])

        parent_path = f",{project['name']},Asset,{asset['sg_asset_type']},"
        yield _get_asset_row(asset, parent_path)


def _get_top_shot_row(project: Map) -> Map:
    return {
        "_id": "Shot",
        "type": "Group",
        "parent": f",{project['name']},",
    }


def _get_top_asset_row(project: Map) -> Map:
    return {
        "_id": "Asset",
        "type": "Group",
        "parent": f",{project['name']},",
    }


def _get_task_row(task: Map, parent_task_path: str) -> Map:
    return {
        "_id": f"{task['content']}_{task['id']}",
        "src_id": task["id"],
        "type": "Task",
        "parent": parent_task_path,
        "task_type": task["step"]["name"],
    }


def _get_asset_row(asset: Map, parent_path: str) -> Map:
    return {
        "_id": asset["code"],
        "src_id": asset["id"],
        "type": "Asset",
        "parent": parent_path,
    }


def _get_shot_row(shot: Map, parent_path: str) -> Map:
    return {
        "_id": shot["code"],
        "src_id": shot["id"],
        "type": "Shot",
        "parent": parent_path,
    }


def _get_asset_group_row(asset: Map, project: Map) -> Map:
    return {
        "_id": asset["sg_asset_type"],
        "type": "Group",
        "parent": f",{project['name']},Asset,",
    }


def _get_episode_shot_group_row(episode: Map, project: Map) -> Map:
    return {
        "_id": episode["name"],
        "type": "Episode",
        "src_id": episode["id"],
        "parent": f",{project['name']},Shot,",
    }


def _get_sequence_shot_group_row(shot: Map, parent_path: str) -> Map:
    return {
        "_id": shot["sg_sequence"]["name"],
        "type": "Sequence",
        "src_id": shot["sg_sequence"]["id"],
        "parent": parent_path,
    }


def _get_project_row(project: Map) -> Map:
    return {
        "_id": project["name"],
        "src_id": project["id"],
        "type": "Project",
        "parent": None,
    }


@timed
def get_hierarchy_by_project(
    project_id: int,
    client: sg.Shotgun,
) -> List[Map]:
    project = client.find_one("Project", [["id", "is", project_id]], ["name"])
    assets = list(_fetch_project_assets(client, project))
    shots = list(_fetch_project_shots(client, project))
    rows_dict = {x["src_id"]: x for x in assets + shots if "src_id" in x}
    tasks = list(_fetch_project_tasks(client, project, rows_dict))

    return [
        _get_project_row(project),
        *assets,
        *shots,
        *tasks,
    ]
