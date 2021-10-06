from typing import Dict, Any

from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridTask,
    ShotgridAsset,
    ShotgridShot,
    ShotgridShotEpisode,
    ShotgridShotSequence,
)
from shotgrid_leecher.record.shotgrid_subtypes import ShotgridProject
from shotgrid_leecher.utils.logger import get_logger

_LOG = get_logger(__name__.split(".")[-1])

Map = Dict[str, Any]


def to_top_shot_row(project: ShotgridProject) -> Map:
    return {
        "_id": ShotgridType.SHOT.value,
        "type": ShotgridType.GROUP.value,
        "parent": f",{project.name},",
    }


def to_top_asset_row(project: ShotgridProject) -> Map:
    return {
        "_id": ShotgridType.ASSET.value,
        "type": ShotgridType.GROUP.value,
        "parent": f",{project.name},",
    }


def to_task_row(task: ShotgridTask, parent_task_path: str) -> Map:
    return {
        "_id": f"{task.content}_{task.id}",
        "src_id": task.id,
        "type": ShotgridType.TASK.value,
        "parent": parent_task_path,
        "task_type": task.step_name(),
    }


def to_asset_row(asset: ShotgridAsset, parent_path: str) -> Map:
    return {
        "_id": asset.code,
        "src_id": asset.id,
        "type": ShotgridType.ASSET.value,
        "parent": parent_path,
    }


def to_shot_row(shot: ShotgridShot, parent_path: str) -> Map:
    return {
        "_id": shot.code,
        "src_id": shot.id,
        # "": shot.cut_duration,
        # "": shot.frame_rate,
        "type": ShotgridType.SHOT.value,
        "parent": parent_path,
    }


def to_asset_group_row(asset_type: str, project: ShotgridProject) -> Map:
    return {
        "_id": asset_type,
        "type": ShotgridType.GROUP.value,
        "parent": f",{project.name},{ShotgridType.ASSET.value},",
    }


def to_episode_shot_group_row(
    episode: ShotgridShotEpisode,
    project: ShotgridProject,
) -> Map:
    return {
        "_id": episode.name,
        "type": ShotgridType.EPISODE.value,
        "src_id": episode.id,
        "parent": f",{project.name},{ShotgridType.SHOT.value},",
    }


def to_sequence_shot_group_row(
    sequence: ShotgridShotSequence, parent_path: str
) -> Map:
    return {
        "_id": sequence.name,
        "type": ShotgridType.SEQUENCE.value,
        "src_id": sequence.id,
        "parent": parent_path,
    }


def to_project_row(project: ShotgridProject) -> Map:
    return {
        "_id": project.name,
        "src_id": project.id,
        "type": ShotgridType.PROJECT.value,
        "parent": None,
    }
