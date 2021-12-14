from functools import reduce
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
from shotgrid_leecher.mapper import query_mapper
from shotgrid_leecher.record.avalon_structures import AvalonProjectData
from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.record.intermediate_structures import IntermediateRow
from shotgrid_leecher.record.queries import (
    ShotgridHierarchyByProjectQuery,
    ShotgridFindAssetsByProjectQuery,
    ShotgridFindShotsByProjectQuery,
    ShotgridFindTasksByProjectQuery,
)
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridShot,
    ShotgridEntityToEntityLink,
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
    rows: Dict[int, IntermediateRow],
    query: ShotgridFindTasksByProjectQuery,
) -> Iterator[IntermediateRow]:
    # TODO: Fields should be configurable
    raw_tasks = entity_repo.find_tasks_for_project(query)
    asset_tasks = [task for task in raw_tasks if task.step]
    for task in asset_tasks:
        key = task.entity.id
        entity_row = rows.get(key)
        if not entity_row:
            continue
        parent_path = f"{entity_row.parent}{entity_row.id},"
        yield mapper.to_task(task, parent_path, query.project_data)


def _patch_up_shot(shot: ShotgridShot) -> ShotgridShot:
    if shot.episode or not shot.sequence:
        return shot
    if not shot.sequence_episode:
        return shot
    return shot.copy_with_episode(shot.sequence_episode)


def _fetch_project_shots(
    query: ShotgridFindShotsByProjectQuery,
) -> Iterator[IntermediateRow]:
    project = query.project
    raw_shots = entity_repo.find_shots_for_project(query)

    if raw_shots:
        yield mapper.to_top_shot(project, query.project_data)

    shots = pipe(
        raw_shots,
        select(_patch_up_shot),
        list,
    )
    yield from _tackle_partial_shots(query.project_data, project, shots)
    yield from _tackle_shot_episodes(query.project_data, project, shots)
    yield from _tackle_shot_sequences(query.project_data, project, shots)
    yield from _tackle_full_shots(query.project_data, project, shots)


def _tackle_full_shots(
    project_data: AvalonProjectData,
    project: ShotgridProject,
    shots: List[ShotgridShot],
) -> Iterator[IntermediateRow]:
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
        yield mapper.to_shot(shot, parent_path, project_data)


def _tackle_shot_sequences(
    project_data: AvalonProjectData,
    project: ShotgridProject,
    shots: List[ShotgridShot],
) -> Iterator[IntermediateRow]:
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
            yield mapper.to_sequence_shot_group(
                shot.sequence, parent_path, project_data
            )


def _tackle_shot_episodes(
    project_data: AvalonProjectData,
    project: ShotgridProject,
    shots: List[ShotgridShot],
) -> Iterator[IntermediateRow]:
    episode_groups = pipe(
        shots,
        where(lambda x: x.episode_name()),
        groupby(lambda x: x.episode_name()),
    )
    for ep, ep_shots in episode_groups.items():
        yield mapper.to_episode_shot_group(
            ep_shots[-1].episode, project, project_data
        )


def _tackle_partial_shots(
    project_data: AvalonProjectData,
    project: ShotgridProject,
    shots: List[ShotgridShot],
) -> Iterator[IntermediateRow]:
    shot_type = ShotgridType.SHOT.value
    partial_shots = pipe(
        shots,
        where(lambda x: not x.sequence_name() or not x.episode_name()),
        list,
    )
    for shot in partial_shots:
        if not shot.episode and not shot.sequence:
            parent_path = f",{project.name},{shot_type},"
            yield mapper.to_shot(shot, parent_path, project_data)
        if not shot.episode and shot.sequence:
            sequence_ = shot.sequence.name
            parent_path = f",{project.name},{shot_type},{sequence_},"
            yield mapper.to_shot(shot, parent_path, project_data)
        if shot.episode and not shot.sequence:
            episode = shot.episode.name
            parent_path = f",{project.name},{shot_type},{episode},"
            yield mapper.to_shot(shot, parent_path, project_data)


def _fetch_project_assets(
    query: ShotgridFindAssetsByProjectQuery,
) -> Iterator[IntermediateRow]:
    # TODO: Fields should be configurable
    project = query.project
    assets = [
        x for x in entity_repo.find_assets_for_project(query) if x.asset_type
    ]
    archetype = ShotgridType.ASSET.value

    if assets:
        yield mapper.to_top_asset(project, query.project_data)

    for g, g_assets in groupby(lambda x: x.asset_type, assets).items():
        yield mapper.to_asset_group(
            g_assets[0].asset_type, project, query.project_data
        )
        for asset in g_assets:
            asset_type = asset.asset_type
            parent_path = f",{project.name},{archetype},{asset_type},"
            yield mapper.to_asset(asset, parent_path, query.project_data)


def _fetch_identified(
    assets: List[IntermediateRow],
    shots: List[IntermediateRow],
) -> Dict[int, IntermediateRow]:
    rows_dict = {
        int(x.src_id): x
        for x in assets + shots
        if x.has_field("src_id") and x.src_id
    }
    return rows_dict


def _fetch_and_link_assets(
    project: ShotgridProject, query: ShotgridHierarchyByProjectQuery
) -> List[IntermediateRow]:
    asset_to_asset_query = (
        query_mapper.hierarchy_to_linked_asset_to_asset_query(project, query)
    )
    links = _reduce_linked_entities(
        entity_repo.find_assets_linked_to_assets(asset_to_asset_query)
    )
    return pipe(
        query_mapper.hierarchy_to_assets_query(project, query),
        _fetch_project_assets,
        select(mapper.to_linked_asset(links)),
        list,
    )


def _fetch_and_link_shots(
    project: ShotgridProject, query: ShotgridHierarchyByProjectQuery
) -> List[IntermediateRow]:
    asset_to_shot_query = query_mapper.hierarchy_to_linked_asset_to_shot_query(
        project, query
    )
    shot_to_shot_query = query_mapper.hierarchy_to_linked_shot_to_shot_query(
        project, query
    )
    links = _reduce_linked_entities(
        entity_repo.find_assets_linked_to_shots(asset_to_shot_query)
        + entity_repo.find_shots_linked_to_shots(shot_to_shot_query)
    )
    return pipe(
        query_mapper.hierarchy_to_shots_query(project, query),
        _fetch_project_shots,
        select(mapper.to_linked_shot(links)),
        list,
    )


def _reduce_linked_entities(
    linked_entities: List[ShotgridEntityToEntityLink],
) -> Dict[int, List[ShotgridEntityToEntityLink]]:
    return reduce(
        lambda agg, x: {**agg, x.child_id: agg.get(x.child_id, []) + [x]},
        linked_entities,
        dict(),
    )


@timed
def get_hierarchy_by_project(
    query: ShotgridHierarchyByProjectQuery,
) -> List[IntermediateRow]:
    steps = entity_repo.find_steps(
        query_mapper.hierarchy_to_steps_query(query)
    )
    project = entity_repo.find_project_by_id(
        query_mapper.hierarchy_to_project_query(query)
    )
    assets = _fetch_and_link_assets(project, query)
    shots = _fetch_and_link_shots(project, query)
    tasks = pipe(
        query_mapper.hierarchy_to_tasks_query(project, query),
        _fetch_project_tasks(_fetch_identified(assets, shots)),
        list,
    )

    return [
        x
        for x in [
            mapper.to_project(project, steps, query.project_data),
            *assets,
            *shots,
            *tasks,
        ]
    ]
