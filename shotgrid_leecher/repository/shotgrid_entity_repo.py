from typing import List, Dict, Any

from toolz import pipe
from toolz.curried import (
    map as select,
)

import shotgrid_leecher.mapper.entity_mapper as mapper
import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.record.queries import (
    ShotgridFindProjectByIdQuery,
    ShotgridFindAssetsByProjectQuery,
    ShotgridFindShotsByProjectQuery,
    ShotgridFindTasksByProjectQuery,
    ShotgridFindAllStepsQuery,
    ShotgridLinkedEntitiesQuery,
)
from shotgrid_leecher.record.shotgrid_filters import (
    CompositeFilter,
    IdFilter,
    IsFilter,
    IsNotFilter,
    NameIsFilter,
)
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridTask,
    ShotgridShot,
    ShotgridAsset,
    ShotgridStep,
)
from shotgrid_leecher.record.shotgrid_subtypes import ShotgridProject

Map = Dict[str, Any]
_F = CompositeFilter
_ID = IdFilter
_IS = IsFilter
_NAMED = NameIsFilter
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


def find_assets_linked_to_shots(
    query: ShotgridLinkedEntitiesQuery,
) -> List[Map]:
    client = conn.get_shotgrid_client()
    fields = list(query.fields_mapping.mapping_table.values())
    raw = client.find(
        ShotgridType.PROJECT.value,
        _F.filter_by(_NAMED("asset.Asset.project", query.project.name)),
        fields,
    )
    pipe(
        raw,
        select(mapper.to_asset_to_shot_link(query.fields_mapping)),
        list,
    )
    return raw


def find_shots_linked_to_shots(
    query: ShotgridLinkedEntitiesQuery,
) -> List[Map]:
    client = conn.get_shotgrid_client()
    fields = list(query.fields_mapping.mapping_table.values())
    raw = client.find(
        ShotgridType.PROJECT.value,
        _F.filter_by(_NAMED("shot.Shot.project", query.project.name)),
        fields,
    )
    return raw


def find_assets_linked_to_assets(
    query: ShotgridLinkedEntitiesQuery,
) -> List[Map]:
    client = conn.get_shotgrid_client()
    fields = list(query.fields_mapping.mapping_table.values())
    raw = client.find(
        ShotgridType.PROJECT.value,
        _F.filter_by(_NAMED("asset.Asset.project", query.project.name)),
        fields,
    )
    return raw


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
    return pipe(
        assets,
        select(
            mapper.to_shotgrid_asset(query.asset_mapping, query.task_mapping)
        ),
        list,
    )


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
    return pipe(
        shots,
        select(mapper.to_shotgrid_shot(query.shot_mapping)),
        list,
    )


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
    return pipe(
        data,
        select(mapper.to_shotgrid_task(query.task_mapping)),
        list,
    )


def find_steps(query: ShotgridFindAllStepsQuery) -> List[ShotgridStep]:
    client = conn.get_shotgrid_client(query.credentials)
    data = client.find(
        ShotgridType.STEP.value,
        [],
        list(query.step_mapping.mapping_table.values()),
    )
    return pipe(
        data,
        select(mapper.to_shotgrid_step(query.step_mapping)),
        list,
    )
