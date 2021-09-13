from typing import Dict, Any, List, Iterator

from toolz import pipe, get_in, curry
from toolz.curried import (
    filter as where,
    map as select,
    unique,
)
from toolz.curried import groupby, get_in as get_in_

import shotgrid_leecher.repository.shotgrid_entity_repo as entity_repo
from shotgrid_leecher.record.queries import (
    ShotgridHierarchyByProjectQuery,
    ShotgridFindProjectByIdQuery,
    ShotgridFindAssetsByProjectQuery,
    ShotgridFindShotsByProjectQuery,
    ShotgridFindTasksByProjectQuery,
)
from shotgrid_leecher.record.shotgrid_subtypes import ShotgridProject
from shotgrid_leecher.utils.logger import get_logger
from shotgrid_leecher.utils.timer import timed

_LOG = get_logger(__name__.split(".")[-1])

Map = Dict[str, Any]


@curry
def _fetch_project_tasks(
    rows: Map,
    query: ShotgridFindTasksByProjectQuery,
) -> Iterator[Map]:
    # TODO: Fields should be configurable
    raw_tasks = entity_repo.find_tasks_for_project(query)
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


def _fetch_project_shots(
    query: ShotgridFindShotsByProjectQuery,
) -> Iterator[Map]:
    # TODO: Fields should be configurable
    project = query.project
    raw_shots = entity_repo.find_shots_for_project(query)

    if raw_shots:
        yield _get_top_shot_row(project)

    shots = pipe(
        raw_shots,
        select(_patch_up_shot),
        list,
    )
    yield from _tackle_partial_shots(project, shots)
    yield from _tackle_shot_episodes(project, shots)
    yield from _tackle_shot_sequences(project, shots)
    yield from _tackle_full_shots(project, shots)


def _tackle_full_shots(
    project: ShotgridProject, shots: List[Map]
) -> Iterator[Map]:
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
        parent_path = f",{project.name},Shot,{episode},{sequence_},"
        yield _get_shot_row(shot, parent_path)


def _tackle_shot_sequences(
    project: ShotgridProject, shots: List[Map]
) -> Iterator[Map]:
    sequence_group = pipe(
        shots,
        where(get_in_("sg_sequence.name".split("."))),
        groupby(get_in_("sg_sequence.name".split("."))),
    )
    for sq, sq_shots in sequence_group.items():
        for shot in unique(sq_shots, get_in_("sg_episode.id".split(".", -1))):
            episode = get_in("sg_episode.name".split("."), shot)
            base_path = f",{project.name},Shot,"
            parent_path = f"{base_path}{episode}," if episode else base_path
            yield _get_sequence_shot_group_row(shot, parent_path)


def _tackle_shot_episodes(
    project: ShotgridProject, shots: List[Map]
) -> Iterator[Map]:
    episode_groups = pipe(
        shots,
        where(get_in_("sg_episode.name".split("."))),
        groupby(get_in_("sg_episode.name".split("."))),
    )
    for ep, ep_shots in episode_groups.items():
        yield _get_episode_shot_group_row(ep_shots[-1]["sg_episode"], project)


def _tackle_partial_shots(
    project: ShotgridProject, shots: List[Map]
) -> Iterator[Map]:
    partial_shots = pipe(
        shots,
        where(
            lambda x: not get_in("sg_sequence.name".split("."), x)
            or not get_in("sg_episode.name".split("."), x)
        ),
        list,
    )
    for shot in partial_shots:
        if not shot.get("sg_episode") and not shot.get("sg_sequence"):
            parent_path = f",{project.name},Shot,"
            yield _get_shot_row(shot, parent_path)
        if not shot.get("sg_episode") and shot.get("sg_sequence"):
            sequence_ = shot.get("sg_sequence")["name"]
            parent_path = f",{project.name},Shot,{sequence_},"
            yield _get_shot_row(shot, parent_path)
        if shot.get("sg_episode") and not shot.get("sg_sequence"):
            episode = shot["sg_episode"]["name"]
            parent_path = f",{project.name},Shot,{episode},"
            yield _get_shot_row(shot, parent_path)


def _fetch_project_assets(
    query: ShotgridFindAssetsByProjectQuery,
) -> Iterator[Map]:
    # TODO: Fields should be configurable
    project = query.project
    assets = entity_repo.find_assets_for_project(query)

    if assets:
        yield _get_top_asset_row(project)

    step = []
    for asset in assets:

        if asset["sg_asset_type"] not in step:
            yield _get_asset_group_row(asset, project)
            step.append(asset["sg_asset_type"])

        parent_path = f",{project.name},Asset,{asset['sg_asset_type']},"
        yield _get_asset_row(asset, parent_path)


def _get_top_shot_row(project: ShotgridProject) -> Map:
    return {
        "_id": "Shot",
        "type": "Group",
        "parent": f",{project.name},",
    }


def _get_top_asset_row(project: ShotgridProject) -> Map:
    return {
        "_id": "Asset",
        "type": "Group",
        "parent": f",{project.name},",
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


def _get_asset_group_row(asset: Map, project: ShotgridProject) -> Map:
    return {
        "_id": asset["sg_asset_type"],
        "type": "Group",
        "parent": f",{project.name},Asset,",
    }


def _get_episode_shot_group_row(episode: Map, project: ShotgridProject) -> Map:
    return {
        "_id": episode["name"],
        "type": "Episode",
        "src_id": episode["id"],
        "parent": f",{project.name},Shot,",
    }


def _get_sequence_shot_group_row(shot: Map, parent_path: str) -> Map:
    return {
        "_id": shot["sg_sequence"]["name"],
        "type": "Sequence",
        "src_id": shot["sg_sequence"]["id"],
        "parent": parent_path,
    }


def _get_project_row(project: ShotgridProject) -> Map:
    return {
        "_id": project.name,
        "src_id": project.id,
        "type": "Project",
        "parent": None,
    }


@timed
def get_hierarchy_by_project(
    query: ShotgridHierarchyByProjectQuery,
) -> List[Map]:
    project = entity_repo.find_project_by_id(
        ShotgridFindProjectByIdQuery.from_query(query)
    )
    assets = pipe(
        ShotgridFindAssetsByProjectQuery.from_query(project, query),
        _fetch_project_assets,
        list,
    )
    shots = pipe(
        ShotgridFindShotsByProjectQuery.from_query(project, query),
        _fetch_project_shots,
        list,
    )
    rows_dict = {x["src_id"]: x for x in assets + shots if "src_id" in x}
    tasks = pipe(
        ShotgridFindTasksByProjectQuery.from_query(project, query),
        _fetch_project_tasks(rows_dict),
        list,
    )

    return [
        _get_project_row(project),
        *assets,
        *shots,
        *tasks,
    ]
