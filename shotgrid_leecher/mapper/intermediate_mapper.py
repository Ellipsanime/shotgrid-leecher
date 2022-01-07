from typing import Dict, Any, cast, List, Optional

import attr
import cattr
from bson import ObjectId
from toolz import curry, memoize

from shotgrid_leecher.record.avalon_structures import AvalonProjectData
from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.record.intermediate_structures import (
    IntermediateGroup,
    IntermediateTask,
    IntermediateAsset,
    IntermediateShot,
    IntermediateEpisode,
    IntermediateSequence,
    IntermediateProject,
    IntermediateParams,
    IntermediateRow,
    IntermediateProjectConfig,
    IntermediateProjectStep,
    IntermediateLinkedEntity,
    IntermediateUser,
)
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridTask,
    ShotgridAsset,
    ShotgridShot,
    ShotgridShotEpisode,
    ShotgridShotSequence,
    ShotgridShotParams,
    ShotgridStep,
    ShotgridEntityToEntityLink,
)
from shotgrid_leecher.record.shotgrid_subtypes import (
    ShotgridProject,
    ShotgridUser,
)
from shotgrid_leecher.utils.collections import keep_keys
from shotgrid_leecher.utils.functional import try_or
from shotgrid_leecher.utils.ids import to_object_id
from shotgrid_leecher.utils.logger import get_logger

Map = Dict[str, Any]

_LOG = get_logger(__name__.split(".")[-1])

_TYPES_MAP: Dict[ShotgridType, type] = {
    ShotgridType.SHOT: IntermediateShot,
    ShotgridType.GROUP: IntermediateGroup,
    ShotgridType.ASSET: IntermediateAsset,
    ShotgridType.PROJECT: IntermediateProject,
    ShotgridType.SEQUENCE: IntermediateSequence,
    ShotgridType.EPISODE: IntermediateEpisode,
    ShotgridType.TASK: IntermediateTask,
}


def to_params(project_data: AvalonProjectData) -> IntermediateParams:
    return IntermediateParams(
        clip_in=project_data.clip_in,
        clip_out=project_data.clip_out,
        fps=project_data.fps,
        frame_end=project_data.frame_end,
        frame_start=project_data.frame_start,
        handle_end=project_data.handle_end,
        handle_start=project_data.handle_start,
        pixel_aspect=project_data.pixel_aspect,
        resolution_height=project_data.resolution_height,
        resolution_width=project_data.resolution_width,
        tools_env=project_data.tools_env,
    )


def _dict_to_params(raw_dic: Map) -> IntermediateParams:
    dic = keep_keys(set(attr.fields_dict(IntermediateParams).keys()), raw_dic)
    return cattr.structure(dic, IntermediateParams)


def to_row(
    raw_dic: Map,
    project_params: IntermediateParams = None,
) -> IntermediateRow:

    has_params = raw_dic.get("params")

    if not has_params and not project_params:
        raise RuntimeError(f"Impossible to get params for {raw_dic}")

    params = try_or(
        lambda: cattr.structure(raw_dic["params"], IntermediateParams),
        project_params,
    )
    dic = {
        **{k.lstrip("_"): v for k, v in raw_dic.items() if k != "type" and v},
        "params": params,
    }
    type_: Any = _TYPES_MAP[ShotgridType(raw_dic["type"])]
    keep = set(attr.fields_dict(type_).keys()).intersection(set(dic.keys()))
    if _has_from_dict(type_):
        return type_.from_dict(keep_keys(keep, dic))
    return type_(**keep_keys(keep, dic))


def to_top_shot(
    project: ShotgridProject, project_data: AvalonProjectData
) -> IntermediateGroup:
    return IntermediateGroup(
        ShotgridType.SHOT.value,
        f",{project.name},",
        to_params(project_data),
        object_id=to_object_id(ShotgridType.SHOT.value),
    )


def to_top_asset(
    project: ShotgridProject, project_data: AvalonProjectData
) -> IntermediateGroup:
    return IntermediateGroup(
        ShotgridType.ASSET.value,
        f",{project.name},",
        to_params(project_data),
        object_id=to_object_id(ShotgridType.ASSET.value),
    )


def to_task(
    task: ShotgridTask,
    parent_task_path: str,
    project_data: AvalonProjectData,
) -> IntermediateTask:

    return IntermediateTask(
        id=f"{task.content}_{task.id}",
        parent=parent_task_path,
        task_type=str(task.step_name()),
        src_id=task.id,
        status=task.status,
        params=to_params(project_data),
        object_id=to_object_id(task.id),
        assigned_users=_to_assigned_users(task.assigned_users),
    )


def to_asset(
    asset: ShotgridAsset,
    parent_path: str,
    project_data: AvalonProjectData,
) -> IntermediateAsset:
    return IntermediateAsset(
        id=asset.code,
        src_id=asset.id,
        parent=parent_path,
        params=to_params(project_data),
        linked_entities=[],
        object_id=to_object_id(asset.id),
    )


def to_shot(
    shot: ShotgridShot,
    parent_path: str,
    project_data: AvalonProjectData,
) -> IntermediateShot:
    result = IntermediateShot(
        id=shot.code,
        src_id=shot.id,
        parent=parent_path,
        params=to_params(project_data),
        linked_entities=[],
        object_id=to_object_id(shot.id),
    )
    if not shot.has_params():
        return result
    raw_params: ShotgridShotParams = cast(ShotgridShotParams, shot.params)
    params = attr.evolve(
        result.params,
        clip_in=raw_params.cut_in or project_data.clip_in,
        clip_out=raw_params.cut_out or project_data.clip_out,
    )
    return attr.evolve(result, params=params)


@curry
def to_linked_shot(
    links_hash: Dict[int, List[ShotgridEntityToEntityLink]],
    shot: IntermediateShot,
) -> IntermediateShot:
    if shot.type != ShotgridType.SHOT:
        return shot
    links = [
        IntermediateLinkedEntity(
            x.parent_id,
            x.type,
            x.quantity,
            to_object_id(x.parent_id),
        )
        for x in links_hash.get(shot.src_id, [])
    ]
    return attr.evolve(shot, linked_entities=links)


@curry
def to_linked_asset(
    links_hash: Dict[int, List[ShotgridEntityToEntityLink]],
    asset: IntermediateAsset,
) -> IntermediateAsset:
    if asset.type != ShotgridType.ASSET:
        return asset
    links = [
        IntermediateLinkedEntity(
            x.parent_id,
            x.type,
            x.quantity,
            to_object_id(x.parent_id),
        )
        for x in links_hash.get(asset.src_id, [])
    ]
    return attr.evolve(asset, linked_entities=links)


def to_asset_group(
    asset_type: str,
    project: ShotgridProject,
    project_data: AvalonProjectData,
) -> IntermediateGroup:
    return IntermediateGroup(
        id=asset_type,
        parent=f",{project.name},{ShotgridType.ASSET.value},",
        params=to_params(project_data),
        object_id=to_object_id(asset_type),
    )


def to_episode_shot_group(
    episode: ShotgridShotEpisode,
    project: ShotgridProject,
    project_data: AvalonProjectData,
) -> IntermediateEpisode:
    return IntermediateEpisode(
        id=episode.name,
        src_id=episode.id,
        parent=f",{project.name},{ShotgridType.SHOT.value},",
        params=to_params(project_data),
        object_id=to_object_id(episode.id),
    )


def to_sequence_shot_group(
    sequence: ShotgridShotSequence,
    parent_path: str,
    project_data: AvalonProjectData,
) -> IntermediateSequence:
    return IntermediateSequence(
        id=sequence.name,
        src_id=sequence.id,
        parent=parent_path,
        params=to_params(project_data),
        object_id=to_object_id(sequence.id),
    )


def to_project(
    project: ShotgridProject,
    steps: List[ShotgridStep],
    project_data: AvalonProjectData,
) -> IntermediateProject:
    project_config = IntermediateProjectConfig(
        steps=[IntermediateProjectStep(x.code, x.short_name) for x in steps]
    )
    return IntermediateProject(
        id=project.name,
        src_id=project.id,
        code=project.code,
        config=project_config,
        params=to_params(project_data),
        object_id=to_object_id(project.id),
    )


def _to_assigned_users(
    users: List[ShotgridUser],
) -> List[IntermediateUser]:
    return [
        IntermediateUser(x.id, to_object_id(x.id), x.type, x.name)
        for x in users
    ]


def _get_parent_id(
    hash_table: Dict[str, IntermediateRow], x: IntermediateRow
) -> Optional[ObjectId]:
    parent = hash_table.get(x.parent)
    if parent:
        return parent.object_id
    return None


@memoize
def _has_from_dict(type_: Any) -> bool:
    return "from_dict" in dir(type_)


def map_parent_ids(rows: List[IntermediateRow]) -> List[IntermediateRow]:
    tree = {f"{x.parent or ','}{x.id},": x for x in rows}
    result = [attr.evolve(x, parent_id=_get_parent_id(tree, x)) for x in rows]
    orphans = [
        x for x in result if not x.parent and x.type != ShotgridType.PROJECT
    ]
    if orphans:
        raise RuntimeError(f"Not all rows have parents {orphans}")
    return result
