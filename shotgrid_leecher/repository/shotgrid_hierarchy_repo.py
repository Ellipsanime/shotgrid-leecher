from typing import Dict, Any, List, Iterator

from toolz import pipe, curry
from toolz.curried import (
    filter as where,
    map as select,
    unique,
)
from toolz.curried import groupby

import shotgrid_leecher.mapper.hierarchy_mapper as mapper
import shotgrid_leecher.repository.shotgrid_entity_repo as entity_repo
from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.record.queries import (
    ShotgridHierarchyByProjectQuery,
    ShotgridFindProjectByIdQuery,
    ShotgridFindAssetsByProjectQuery,
    ShotgridFindShotsByProjectQuery,
    ShotgridFindTasksByProjectQuery,
)
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridShot,
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
    rows: Dict[int, Any],
    query: ShotgridFindTasksByProjectQuery,
) -> Iterator[Map]:
    # TODO: Fields should be configurable
    raw_tasks = entity_repo.find_tasks_for_project(query)
    asset_tasks = [task for task in raw_tasks if task.step]
    for task in asset_tasks:
        key = task.entity.id
        entity_row = rows.get(key)
        if not entity_row:
            continue
        parent_path = f"{entity_row['parent']}{entity_row['_id']},"
        yield mapper.to_task_row(task, parent_path)


def _patch_up_shot(shot: ShotgridShot) -> ShotgridShot:
    if shot.episode or not shot.sequence:
        return shot
    if not shot.sequence_episode:
        return shot
    return shot.copy_with_episode(shot.sequence_episode)


def _fetch_project_shots(
    query: ShotgridFindShotsByProjectQuery,
) -> Iterator[Map]:
    # TODO: Fields should be configurable
    project = query.project
    raw_shots = entity_repo.find_shots_for_project(query)

    if raw_shots:
        yield mapper.to_top_shot_row(project)

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
    shot_type = ShotgridType.SHOT.value
    full_shots = pipe(
        shots,
        where(lambda x: x.sequence_name() and x.episode_name()),
        list,
    )
    for shot in full_shots:
        episode = shot.episode_name()
        sequence_ = shot.sequence_name()
        parent_path = f",{project.name},{shot_type},{episode},{sequence_},"
        yield mapper.to_shot_row(shot, parent_path)


def _tackle_shot_sequences(
    project: ShotgridProject,
    shots: List[ShotgridShot],
) -> Iterator[Map]:
    shot_type = ShotgridType.SHOT.value
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
            yield mapper.to_sequence_shot_group_row(shot.sequence, parent_path)


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
        yield mapper.to_episode_shot_group_row(ep_shots[-1].episode, project)


def _tackle_partial_shots(
    project: ShotgridProject,
    shots: List[ShotgridShot],
) -> Iterator[Map]:
    shot_type = ShotgridType.SHOT.value
    partial_shots = pipe(
        shots,
        where(lambda x: not x.sequence_name() or not x.episode_name()),
        list,
    )
    for shot in partial_shots:
        if not shot.episode and not shot.sequence:
            parent_path = f",{project.name},{shot_type},"
            yield mapper.to_shot_row(shot, parent_path)
        if not shot.episode and shot.sequence:
            sequence_ = shot.sequence.name
            parent_path = f",{project.name},{shot_type},{sequence_},"
            yield mapper.to_shot_row(shot, parent_path)
        if shot.episode and not shot.sequence:
            episode = shot.episode.name
            parent_path = f",{project.name},{shot_type},{episode},"
            yield mapper.to_shot_row(shot, parent_path)


def _fetch_project_assets(
    query: ShotgridFindAssetsByProjectQuery,
) -> Iterator[Map]:
    # TODO: Fields should be configurable
    project = query.project
    assets = entity_repo.find_assets_for_project(query)
    archetype = ShotgridType.ASSET.value

    if assets:
        yield mapper.to_top_asset_row(project)

    for g, g_assets in groupby(lambda x: x.asset_type, assets).items():
        yield mapper.to_asset_group_row(g_assets[0].asset_type, project)
        for asset in g_assets:
            asset_type = asset.asset_type
            parent_path = f",{project.name},{archetype},{asset_type},"
            yield mapper.to_asset_row(asset, parent_path)


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
    rows_dict = {int(x["src_id"]): x for x in assets + shots if "src_id" in x}
    tasks = pipe(
        ShotgridFindTasksByProjectQuery.from_query(project, query),
        _fetch_project_tasks(rows_dict),
        list,
    )

    return [
        mapper.to_project_row(project),
        *assets,
        *shots,
        *tasks,
    ]
