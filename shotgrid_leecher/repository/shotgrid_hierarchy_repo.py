from typing import Dict, Any, List, Iterator

from toolz import pipe, curry
from toolz.curried import (
    filter as where,
    map as select,
    unique,
)
from toolz.curried import groupby

import shotgrid_leecher.repository.shotgrid_entity_repo as entity_repo
from shotgrid_leecher.record.enums import ShotgridTypes, ShotgridField
from shotgrid_leecher.record.queries import (
    ShotgridHierarchyByProjectQuery,
    ShotgridFindProjectByIdQuery,
    ShotgridFindAssetsByProjectQuery,
    ShotgridFindShotsByProjectQuery,
    ShotgridFindTasksByProjectQuery,
)
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridTask,
    ShotgridShot,
    ShotgridShotEpisode,
    ShotgridShotSequence,
)
from shotgrid_leecher.record.shotgrid_subtypes import (
    ShotgridProject,
)
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
    asset_tasks = [task for task in raw_tasks if task.step]
    for task in asset_tasks:
        key = task.entity.id
        entity_row = rows.get(str(key), rows.get(key))
        if not entity_row:
            continue
        parent_path = f"{entity_row['parent']}{entity_row['_id']},"
        yield _get_task_row(task, parent_path)


def _patch_up_shot(shot: ShotgridShot) -> ShotgridShot:
    if shot.episode or not shot.sequence:
        return shot
    return shot.copy_with_episode(shot.sequence_episode)


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
    project: ShotgridProject,
    shots: List[ShotgridShot],
) -> Iterator[Map]:
    shot_type = ShotgridTypes.SHOT.value
    full_shots = pipe(
        shots,
        where(lambda x: x.sequence_name() and x.episode_name()),
        list,
    )
    for shot in full_shots:
        episode = shot.episode_name()
        sequence_ = shot.sequence_name()
        parent_path = f",{project.name},{shot_type},{episode},{sequence_},"
        yield _get_shot_row(shot, parent_path)


def _tackle_shot_sequences(
    project: ShotgridProject,
    shots: List[ShotgridShot],
) -> Iterator[Map]:
    shot_type = ShotgridTypes.SHOT.value
    sequence_group = pipe(
        shots,
        where(lambda x: x.sequence_name()),
        groupby(lambda x: x.sequence_name()),
    )
    for sq, sq_shots in sequence_group.items():
        for shot in unique(sq_shots, lambda x: x.episode_id()):
            episode = shot.episode_name()
            base_path = f",{project.name},{shot_type},"
            parent_path = f"{base_path}{episode}," if episode else base_path
            yield _get_sequence_shot_group_row(shot.sequence, parent_path)


def _tackle_shot_episodes(
    project: ShotgridProject,
    shots: List[ShotgridShot],
) -> Iterator[Map]:
    episode_groups = pipe(
        shots,
        where(lambda x: x.episode_name()),
        groupby(lambda x: x.episode_name()),
    )
    for ep, ep_shots in episode_groups.items():
        yield _get_episode_shot_group_row(ep_shots[-1].episode, project)


def _tackle_partial_shots(
    project: ShotgridProject,
    shots: List[ShotgridShot],
) -> Iterator[Map]:
    shot_type = ShotgridTypes.SHOT.value
    partial_shots = pipe(
        shots,
        where(lambda x: not x.sequence_name() or not x.episode_name()),
        list,
    )
    for shot in partial_shots:
        if not shot.episode and not shot.sequence:
            parent_path = f",{project.name},{shot_type},"
            yield _get_shot_row(shot, parent_path)
        if not shot.episode and shot.sequence:
            sequence_ = shot.sequence.name
            parent_path = f",{project.name},{shot_type},{sequence_},"
            yield _get_shot_row(shot, parent_path)
        if shot.episode and not shot.sequence:
            episode = shot.episode.name
            parent_path = f",{project.name},{shot_type},{episode},"
            yield _get_shot_row(shot, parent_path)


def _fetch_project_assets(
    query: ShotgridFindAssetsByProjectQuery,
) -> Iterator[Map]:
    # TODO: Fields should be configurable
    project = query.project
    assets = entity_repo.find_assets_for_project(query)
    asset_type_field = query.asset_mapping.value(ShotgridField.ASSET_TYPE)
    asset_type = ShotgridTypes.ASSET.value

    if assets:
        yield _get_top_asset_row(project)

    for g, g_assets in groupby(asset_type_field, assets).items():
        yield _get_asset_group_row(g_assets[0][asset_type_field], project)
        for asset in g_assets:
            asset_value = asset[asset_type_field]
            parent_path = f",{project.name},{asset_type},{asset_value},"
            yield _get_asset_row(asset, parent_path)


def _get_top_shot_row(project: ShotgridProject) -> Map:
    return {
        "_id": ShotgridTypes.SHOT.value,
        "type": ShotgridTypes.GROUP.value,
        "parent": f",{project.name},",
    }


def _get_top_asset_row(project: ShotgridProject) -> Map:
    return {
        "_id": ShotgridTypes.ASSET.value,
        "type": ShotgridTypes.GROUP.value,
        "parent": f",{project.name},",
    }


def _get_task_row(task: ShotgridTask, parent_task_path: str) -> Map:
    return {
        "_id": f"{task.content}_{task.id}",
        "src_id": task.id,
        "type": ShotgridTypes.TASK.value,
        "parent": parent_task_path,
        "task_type": task.step.name,
    }


def _get_asset_row(asset: Map, parent_path: str) -> Map:
    return {
        "_id": asset["code"],
        "src_id": asset["id"],
        "type": ShotgridTypes.ASSET.value,
        "parent": parent_path,
    }


def _get_shot_row(shot: ShotgridShot, parent_path: str) -> Map:
    return {
        "_id": shot.code,
        "src_id": shot.id,
        "type": ShotgridTypes.SHOT.value,
        "parent": parent_path,
    }


def _get_asset_group_row(asset_type: str, project: ShotgridProject) -> Map:
    return {
        "_id": asset_type,
        "type": ShotgridTypes.GROUP.value,
        "parent": f",{project.name},{ShotgridTypes.ASSET.value},",
    }


def _get_episode_shot_group_row(
    episode: ShotgridShotEpisode,
    project: ShotgridProject,
) -> Map:
    return {
        "_id": episode.name,
        "type": ShotgridTypes.EPISODE.value,
        "src_id": episode.id,
        "parent": f",{project.name},{ShotgridTypes.SHOT.value},",
    }


def _get_sequence_shot_group_row(
    sequence: ShotgridShotSequence, parent_path: str
) -> Map:
    return {
        "_id": sequence.name,
        "type": ShotgridTypes.SEQUENCE.value,
        "src_id": sequence.id,
        "parent": parent_path,
    }


def _get_project_row(project: ShotgridProject) -> Map:
    return {
        "_id": project.name,
        "src_id": project.id,
        "type": ShotgridTypes.PROJECT.value,
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
