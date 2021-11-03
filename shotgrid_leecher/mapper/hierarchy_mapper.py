from typing import Dict, Any, cast

import attr

from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.record.intermediate_structures import (
    IntermediateTopShot,
    IntermediateTopAsset,
    IntermediateTask,
    IntermediateAsset,
    IntermediateShot,
    IntermediateShotParams,
    IntermediateAssetGroup,
    IntermediateEpisode,
    IntermediateSequence,
    IntermediateProject,
)
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridTask,
    ShotgridAsset,
    ShotgridShot,
    ShotgridShotEpisode,
    ShotgridShotSequence,
    ShotgridShotParams,
)
from shotgrid_leecher.record.shotgrid_subtypes import ShotgridProject
from shotgrid_leecher.utils.logger import get_logger

_LOG = get_logger(__name__.split(".")[-1])

Map = Dict[str, Any]


def to_top_shot_row(project: ShotgridProject) -> IntermediateTopShot:
    return IntermediateTopShot(ShotgridType.SHOT.value, f",{project.name},")


def to_top_asset_row(project: ShotgridProject) -> IntermediateTopAsset:
    return IntermediateTopAsset(ShotgridType.ASSET.value, f",{project.name},")


def to_task_row(task: ShotgridTask, parent_task_path: str) -> IntermediateTask:
    return IntermediateTask(
        id=f"{task.content}_{task.id}",
        parent=parent_task_path,
        task_type=task.step_name(),
        src_id=task.id,
    )


def to_asset_row(asset: ShotgridAsset, parent_path: str) -> IntermediateAsset:
    return IntermediateAsset(
        id=asset.code,
        src_id=asset.id,
        parent=parent_path,
    )


def to_shot_row(shot: ShotgridShot, parent_path: str) -> IntermediateShot:
    result = IntermediateShot(
        id=shot.code,
        src_id=shot.id,
        parent=parent_path,
        params=None,
    )
    if not shot.has_params():
        return result
    raw_params: ShotgridShotParams = cast(ShotgridShotParams, shot.params)
    params = IntermediateShotParams(
        clip_in=raw_params.cut_in,
        clip_out=raw_params.cut_out,
    )
    return attr.evolve(result, params=params)


def to_asset_group_row(
    asset_type: str,
    project: ShotgridProject,
) -> IntermediateAssetGroup:
    return IntermediateAssetGroup(
        id=asset_type,
        parent=f",{project.name},{ShotgridType.ASSET.value},",
    )


def to_episode_shot_group_row(
    episode: ShotgridShotEpisode,
    project: ShotgridProject,
) -> IntermediateEpisode:
    return IntermediateEpisode(
        id=episode.name,
        src_id=episode.id,
        parent=f",{project.name},{ShotgridType.SHOT.value},",
    )


def to_sequence_shot_group_row(
    sequence: ShotgridShotSequence, parent_path: str
) -> IntermediateSequence:
    return IntermediateSequence(
        id=sequence.name,
        src_id=sequence.id,
        parent=parent_path,
    )


def to_project_row(project: ShotgridProject) -> IntermediateProject:
    return IntermediateProject(
        id=project.name,
        src_id=project.id,
    )
