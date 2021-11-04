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
    IntermediateAssetGroup,
    IntermediateEpisode,
    IntermediateSequence,
    IntermediateProject,
    IntermediateParams,
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


def _to_params(project_data: AvalonProjectData) -> IntermediateParams:
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


def to_top_shot(
    project: ShotgridProject, project_data: AvalonProjectData
) -> IntermediateTopShot:
    return IntermediateTopShot(
        ShotgridType.SHOT.value, f",{project.name},", _to_params(project_data)
    )


def to_top_asset(
    project: ShotgridProject, project_data: AvalonProjectData
) -> IntermediateTopAsset:
    return IntermediateTopAsset(
        ShotgridType.ASSET.value, f",{project.name},", _to_params(project_data)
    )


def to_task(
    task: ShotgridTask,
    parent_task_path: str,
    project_data: AvalonProjectData,
) -> IntermediateTask:
    return IntermediateTask(
        id=f"{task.content}_{task.id}",
        parent=parent_task_path,
        task_type=str(task.step_name),
        src_id=task.id,
        params=_to_params(project_data),
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
        params=_to_params(project_data),
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
        params=_to_params(project_data),
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


def to_asset_group(
    asset_type: str,
    project: ShotgridProject,
    project_data: AvalonProjectData,
) -> IntermediateAssetGroup:
    return IntermediateAssetGroup(
        id=asset_type,
        parent=f",{project.name},{ShotgridType.ASSET.value},",
        params=_to_params(project_data),
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
        params=_to_params(project_data),
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
        params=_to_params(project_data),
    )


def to_project(
    project: ShotgridProject,
    project_data: AvalonProjectData,
) -> IntermediateProject:
    return IntermediateProject(
        id=project.name,
        src_id=project.id,
        params=_to_params(project_data),
    )
