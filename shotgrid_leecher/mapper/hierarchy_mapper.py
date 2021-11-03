from typing import Dict, Any, cast

import attr

from shotgrid_leecher.record.avalon_structures import AvalonProjectData
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


def to_top_shot(
    project: ShotgridProject, project_data: AvalonProjectData
) -> IntermediateTopShot:
    print(project_data)
    return IntermediateTopShot(ShotgridType.SHOT.value, f",{project.name},")


def to_top_asset(
    project: ShotgridProject, project_data: AvalonProjectData
) -> IntermediateTopAsset:
    print(project_data)
    return IntermediateTopAsset(ShotgridType.ASSET.value, f",{project.name},")


def to_task(
    task: ShotgridTask,
    parent_task_path: str,
    project_data: AvalonProjectData,
) -> IntermediateTask:
    print(project_data)
    return IntermediateTask(
        id=f"{task.content}_{task.id}",
        parent=parent_task_path,
        task_type=task.step_name,
        src_id=task.id,
    )


def to_asset(
    asset: ShotgridAsset,
    parent_path: str,
    project_data: AvalonProjectData,
) -> IntermediateAsset:
    print(project_data)
    return IntermediateAsset(
        id=asset.code,
        src_id=asset.id,
        parent=parent_path,
    )


def to_shot(
    shot: ShotgridShot,
    parent_path: str,
    project_data: AvalonProjectData,
) -> IntermediateShot:
    print(project_data)
    result = IntermediateShot(
        id=shot.code,
        src_id=shot.id,
        parent=parent_path,
        params=None,
    )
    if not shot.has_params:
        return result
    raw_params: ShotgridShotParams = cast(ShotgridShotParams, shot.params)
    params = IntermediateShotParams(
        clip_in=raw_params.cut_in,
        clip_out=raw_params.cut_out,
    )
    return attr.evolve(result, params=params)


def to_asset_group(
    asset_type: str,
    project: ShotgridProject,
    project_data: AvalonProjectData,
) -> IntermediateAssetGroup:
    print(project_data)
    return IntermediateAssetGroup(
        id=asset_type,
        parent=f",{project.name},{ShotgridType.ASSET.value},",
    )


def to_episode_shot_group(
    episode: ShotgridShotEpisode,
    project: ShotgridProject,
    project_data: AvalonProjectData,
) -> IntermediateEpisode:
    print(project_data)
    return IntermediateEpisode(
        id=episode.name,
        src_id=episode.id,
        parent=f",{project.name},{ShotgridType.SHOT.value},",
    )


def to_sequence_shot_group(
    sequence: ShotgridShotSequence,
    parent_path: str,
    project_data: AvalonProjectData,
) -> IntermediateSequence:
    print(project_data)
    return IntermediateSequence(
        id=sequence.name,
        src_id=sequence.id,
        parent=parent_path,
    )


def to_project(
    project: ShotgridProject,
    project_data: AvalonProjectData,
) -> IntermediateProject:
    print(project_data)
    return IntermediateProject(
        id=project.name,
        src_id=project.id,
    )
