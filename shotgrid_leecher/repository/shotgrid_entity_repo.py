from typing import List

import shotgrid_leecher.mapper.entity_mapper as mapper
import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.record.queries import (
    ShotgridFindProjectByIdQuery,
    ShotgridFindAssetsByProjectQuery,
    ShotgridFindShotsByProjectQuery,
    ShotgridFindTasksByProjectQuery,
    ShotgridFindAllStepsQuery,
)
from shotgrid_leecher.record.shotgrid_filters import (
    CompositeFilter,
    IdFilter,
    IsFilter,
    IsNotFilter,
)
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridTask,
    ShotgridShot,
    ShotgridAsset,
    ShotgridStep,
)
from shotgrid_leecher.record.shotgrid_subtypes import ShotgridProject

_F = CompositeFilter
_ID = IdFilter
_IS = IsFilter
_NOT = IsNotFilter


def find_project_by_id(query: ShotgridFindProjectByIdQuery) -> ShotgridProject:
    client = conn.get_shotgrid_client(query.credentials)
    fields = list(query.project_mapping.mapping_table.values())
    raw = client.find_one(
        ShotgridType.PROJECT.value,
        _F.filter_by(_ID(query.project_id)),
        fields,
    )
    return mapper.to_shotgrid_project(query.project_mapping, raw)


def find_assets_for_project(
    query: ShotgridFindAssetsByProjectQuery,
) -> List[ShotgridAsset]:
    client = conn.get_shotgrid_client(query.credentials)

    assets = client.find(
        ShotgridType.ASSET.value,
        _F.filter_by(
            _IS(ShotgridType.PROJECT.value.lower(), query.project.to_dict())
        ),
        list(query.asset_mapping.mapping_table.values()),
    )
    return [
        mapper.to_shotgrid_asset(query.asset_mapping, query.task_mapping, x)
        for x in assets
    ]


def find_shots_for_project(
    query: ShotgridFindShotsByProjectQuery,
) -> List[ShotgridShot]:
    client = conn.get_shotgrid_client(query.credentials)
    shots = client.find(
        ShotgridType.SHOT.value,
        _F.filter_by(
            _IS(ShotgridType.PROJECT.value.lower(), query.project.to_dict())
        ),
        list(query.shot_mapping.mapping_table.values()),
    )
    return [mapper.to_shotgrid_shot(query.shot_mapping, x) for x in shots]


def find_tasks_for_project(
    query: ShotgridFindTasksByProjectQuery,
) -> List[ShotgridTask]:
    client = conn.get_shotgrid_client(query.credentials)
    data = client.find(
        ShotgridType.TASK.value,
        _F.filter_by(
            _IS(ShotgridType.PROJECT.value.lower(), query.project.to_dict()),
            _NOT("entity", None),
        ),
        list(query.task_mapping.mapping_table.values()),
    )
    return [mapper.to_shotgrid_task(query.task_mapping, x) for x in data]


def find_steps(query: ShotgridFindAllStepsQuery) -> List[ShotgridStep]:
    client = conn.get_shotgrid_client(query.credentials)
    data = client.find(
        ShotgridType.STEP.value,
        [],
        list(query.step_mapping.mapping_table.values()),
    )
    return [mapper.to_shotgrid_step(query.step_mapping, x) for x in data]
