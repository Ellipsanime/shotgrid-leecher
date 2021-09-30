from typing import List, Dict, Any

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.mapper.entity_mapper import to_shotgrid_task, \
    to_shotgrid_shot
from shotgrid_leecher.record.enums import ShotgridTypes
from shotgrid_leecher.record.queries import (
    ShotgridFindProjectByIdQuery,
    ShotgridFindAssetsByProjectQuery,
    ShotgridFindShotsByProjectQuery, ShotgridFindTasksByProjectQuery,
)
from shotgrid_leecher.record.shotgrid_filters import (
    CompositeFilter,
    IdFilter,
    IsFilter,
    IsNotFilter,
)
from shotgrid_leecher.record.shotgrid_structures import ShotgridTask, \
    ShotgridShot
from shotgrid_leecher.record.shotgrid_subtypes import ShotgridProject

_F = CompositeFilter
_ID = IdFilter
_IS = IsFilter
_NOT = IsNotFilter


def find_project_by_id(query: ShotgridFindProjectByIdQuery) -> ShotgridProject:
    client = conn.get_shotgrid_client(query.credentials)
    fields = list(query.project_mapping.mapping_table.values())
    raw = client.find_one(
        ShotgridTypes.PROJECT.value,
        _F.filter_by(_ID(query.project_id)),
        fields,
    )
    return ShotgridProject.from_dict(raw)


def find_assets_for_project(
    query: ShotgridFindAssetsByProjectQuery,
) -> List[Dict[str, Any]]:
    client = conn.get_shotgrid_client(query.credentials)
    return client.find(
        ShotgridTypes.ASSET.value,
        _F.filter_by(
            _IS(ShotgridTypes.PROJECT.value.lower(), query.project.to_dict())
        ),
        list(query.asset_mapping.mapping_table.values()),
    )


def find_shots_for_project(
    query: ShotgridFindShotsByProjectQuery,
) -> List[ShotgridShot]:
    client = conn.get_shotgrid_client(query.credentials)
    shots = client.find(
        ShotgridTypes.SHOT.value,
        _F.filter_by(
            _IS(ShotgridTypes.PROJECT.value.lower(), query.project.to_dict())
        ),
        list(query.shot_mapping.mapping_table.values()),
    )
    return [to_shotgrid_shot(query.shot_mapping, x) for x in shots]


def find_tasks_for_project(
    query: ShotgridFindTasksByProjectQuery
) -> List[ShotgridTask]:
    client = conn.get_shotgrid_client(query.credentials)
    data = client.find(
        ShotgridTypes.TASK.value,
        _F.filter_by(
            _IS(ShotgridTypes.PROJECT.value.lower(), query.project.to_dict()),
            _NOT("entity", None),
        ),
        list(query.task_mapping.mapping_table.values())
    )
    return [to_shotgrid_task(query.task_mapping, x) for x in data]
