from typing import Dict, Any, List, Iterator

from toolz import pipe, get_in, curry
from toolz.curried import (
    filter as where,
    map as select,
    unique,
)
from toolz.curried import groupby, get_in as get_in_

import shotgrid_leecher.repository.shotgrid_entity_repo as entity_repo
from shotgrid_leecher.record.enums import ShotgridTypes
from shotgrid_leecher.record.queries import (
    ShotgridHierarchyByProjectQuery,
    ShotgridFindProjectByIdQuery,
    ShotgridFindAssetsByProjectQuery,
    ShotgridFindShotsByProjectQuery,
    ShotgridFindTasksByProjectQuery,
)
from shotgrid_leecher.record.shotgrid_structures import ShotgridTask
from shotgrid_leecher.record.shotgrid_subtypes import (
    ShotgridProject,
    ShotFieldMapping,
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


@curry
def _patch_up_shot(fields_mapping: ShotFieldMapping, shot: Map) -> Map:
    if shot.get(fields_mapping.episode()) or not shot.get(
        fields_mapping.sequence_episode()
    ):
        return shot
    return {
        **shot,
        fields_mapping.episode(): shot[fields_mapping.sequence_episode()],
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
        select(_patch_up_shot(query.shot_mapping)),
        list,
    )
    yield from _tackle_partial_shots(project, shots, query.shot_mapping)
    yield from _tackle_shot_episodes(project, shots, query.shot_mapping)
    yield from _tackle_shot_sequences(project, shots, query.shot_mapping)
    yield from _tackle_full_shots(project, shots, query.shot_mapping)


def _tackle_full_shots(
    project: ShotgridProject,
    shots: List[Map],
    fields_mapping: ShotFieldMapping,
) -> Iterator[Map]:
    full_shots = pipe(
        shots,
        where(
            lambda x: get_in([fields_mapping.sequence(), "name"], x)
            and get_in([fields_mapping.episode(), "name"], x)
        ),
        list,
    )
    for shot in full_shots:
        episode = shot[fields_mapping.episode()]["name"]
        sequence_ = shot[fields_mapping.sequence()]["name"]
        parent_path = f",{project.name},Shot,{episode},{sequence_},"
        yield _get_shot_row(shot, parent_path)


def _tackle_shot_sequences(
    project: ShotgridProject,
    shots: List[Map],
    fields_mapping: ShotFieldMapping,
) -> Iterator[Map]:
    sequence_group = pipe(
        shots,
        where(get_in_([fields_mapping.sequence(), "name"])),
        groupby(get_in_([fields_mapping.sequence(), "name"])),
    )
    for sq, sq_shots in sequence_group.items():
        get_unique_ids = get_in_([fields_mapping.episode(), "id"])
        for shot in unique(sq_shots, get_unique_ids):
            episode = get_in([fields_mapping.episode(), "name"], shot)
            base_path = f",{project.name},Shot,"
            parent_path = f"{base_path}{episode}," if episode else base_path
            yield _get_sequence_shot_group_row(
                shot[fields_mapping.sequence()],
                parent_path,
            )


def _tackle_shot_episodes(
    project: ShotgridProject,
    shots: List[Map],
    fields_mapping: ShotFieldMapping,
) -> Iterator[Map]:
    episode_groups = pipe(
        shots,
        where(get_in_([fields_mapping.episode(), "name"])),
        groupby(get_in_([fields_mapping.episode(), "name"])),
    )
    for ep, ep_shots in episode_groups.items():
        yield _get_episode_shot_group_row(
            ep_shots[-1][fields_mapping.episode()], project
        )


def _tackle_partial_shots(
    project: ShotgridProject,
    shots: List[Map],
    fields_mapping: ShotFieldMapping,
) -> Iterator[Map]:
    sequence_key = fields_mapping.sequence()
    episode_key = fields_mapping.episode()
    partial_shots = pipe(
        shots,
        where(
            lambda x: not get_in([sequence_key, "name"], x)
            or not get_in([episode_key, "name"], x)
        ),
        list,
    )
    for shot in partial_shots:
        if not shot.get(episode_key) and not shot.get(sequence_key):
            parent_path = f",{project.name},Shot,"
            yield _get_shot_row(shot, parent_path)
        if not shot.get(episode_key) and shot.get(sequence_key):
            sequence_ = shot.get(sequence_key)["name"]
            parent_path = f",{project.name},Shot,{sequence_},"
            yield _get_shot_row(shot, parent_path)
        if shot.get(episode_key) and not shot.get(sequence_key):
            episode = shot[episode_key]["name"]
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

    asset_type_field = query.asset_mapping.asset_type()
    for g, g_assets in groupby(asset_type_field, assets).items():
        yield _get_asset_group_row(g_assets[0][asset_type_field], project)
        for asset in g_assets:
            parent_path = f",{project.name},Asset,{asset[asset_type_field]},"
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


def _get_shot_row(shot: Map, parent_path: str) -> Map:
    return {
        "_id": shot["code"],
        "src_id": shot["id"],
        "type": ShotgridTypes.SHOT.value,
        "parent": parent_path,
    }


def _get_asset_group_row(asset_type: str, project: ShotgridProject) -> Map:
    return {
        "_id": asset_type,
        "type": ShotgridTypes.GROUP.value,
        "parent": f",{project.name},{ShotgridTypes.ASSET.value},",
    }


def _get_episode_shot_group_row(episode: Map, project: ShotgridProject) -> Map:
    return {
        "_id": episode["name"],
        "type": ShotgridTypes.EPISODE.value,
        "src_id": episode["id"],
        "parent": f",{project.name},{ShotgridTypes.SHOT.value},",
    }


def _get_sequence_shot_group_row(shot_sequence: Map, parent_path: str) -> Map:
    return {
        "_id": shot_sequence["name"],
        "type": ShotgridTypes.SEQUENCE.value,
        "src_id": shot_sequence["id"],
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
