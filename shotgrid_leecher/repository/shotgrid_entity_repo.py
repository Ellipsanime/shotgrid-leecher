from typing import List, Dict, Any

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.enums import ShotgridTypes
from shotgrid_leecher.record.shotgrid_filters import (
    CompositeFilter,
    IdFilter,
    IsFilter,
    IsNotFilter,
)
from shotgrid_leecher.record.shotgrid_subtypes import ShotgridProject

_F = CompositeFilter
_ID = IdFilter
_IS = IsFilter
_NOT = IsNotFilter


def find_project_by_id(project_id: int) -> ShotgridProject:
    client = conn.get_shotgrid_client()
    fields = ["name"]
    raw = client.find_one(
        ShotgridTypes.PROJECT.value,
        _F.filter_by(_ID(project_id)),
        fields,
    )
    return ShotgridProject.from_dict(raw)


def find_assets_for_project(project: ShotgridProject) -> List[Dict[str, Any]]:
    client = conn.get_shotgrid_client()
    return client.find(
        ShotgridTypes.ASSET.value,
        _F.filter_by(
            _IS(ShotgridTypes.PROJECT.value.lower(), project.to_dict())
        ),
        ["code", "sg_asset_type"],
    )


def find_shots_for_project(project: ShotgridProject) -> List[Dict[str, Any]]:
    client = conn.get_shotgrid_client()
    return client.find(
        ShotgridTypes.SHOT.value,
        _F.filter_by(_IS(ShotgridTypes.PROJECT.value.lower(), project.to_dict())),
        [
            "sg_sequence",
            "sg_episode",
            "sg_cut_duration",
            "sg_frame_rate",
            "sg_sequence.Sequence.episode",
            "code",
        ],
    )


def find_tasks_for_project(project: ShotgridProject) -> List[Dict[str, Any]]:
    client = conn.get_shotgrid_client()
    return client.find(
        ShotgridTypes.TASK.value,
        _F.filter_by(
            _IS(ShotgridTypes.PROJECT.value.lower(), project.to_dict()),
            _NOT("entity", None),
        ),
        ["content", "name", "id", "step", "entity"],
    )