from typing import Callable

from toolz import curry

from record.enums import QueryStringType
from record.http_models import ScheduleQueryParams
from record.queries import (
    ShotgridHierarchyByProjectQuery,
    ShotgridFindProjectByIdQuery,
    ShotgridFindAssetsByProjectQuery,
    ShotgridFindTasksByProjectQuery,
    ShotgridFindShotsByProjectQuery,
    FindEntityQuery,
    ShotgridFindAllStepsQuery,
    ShotgridLinkedEntitiesQuery,
)
from record.shotgrid_subtypes import ShotgridProject


def http_to_find_query(model: ScheduleQueryParams) -> FindEntityQuery:
    to_type: Callable = QueryStringType.from_param(
        model.filter_value_type or ""
    ).value
    filters = (
        {str(model.filter_field): to_type(model.filter_value)}
        if (bool(model.filter_value) and bool(model.filter_field))
        else dict()
    )
    sorts = (
        [(model.sort_field, int(model.sort_order or 1))]
        if model.sort_field
        else []
    )
    return FindEntityQuery(
        filter=filters,
        sort=sorts,
        skip=model.skip,
        limit=model.limit,
    )


def hierarchy_to_project_query(
    entity: ShotgridHierarchyByProjectQuery,
) -> ShotgridFindProjectByIdQuery:
    return ShotgridFindProjectByIdQuery(
        project_id=entity.project_id,
        credentials=entity.credentials,
        project_mapping=entity.fields_mapping.project,
        project_data=entity.project_data,
    )


def hierarchy_to_steps_query(
    query: ShotgridHierarchyByProjectQuery,
) -> ShotgridFindAllStepsQuery:
    return ShotgridFindAllStepsQuery(
        credentials=query.credentials,
        step_mapping=query.fields_mapping.step,
    )


@curry
def hierarchy_to_assets_query(
    project: ShotgridProject, query: ShotgridHierarchyByProjectQuery
) -> ShotgridFindAssetsByProjectQuery:
    return ShotgridFindAssetsByProjectQuery(
        project=project,
        credentials=query.credentials,
        asset_mapping=query.fields_mapping.asset,
        task_mapping=query.fields_mapping.task,
        project_data=query.project_data,
    )


@curry
def hierarchy_to_shots_query(
    project: ShotgridProject,
    query: ShotgridHierarchyByProjectQuery,
) -> ShotgridFindShotsByProjectQuery:
    return ShotgridFindShotsByProjectQuery(
        project=project,
        credentials=query.credentials,
        shot_mapping=query.fields_mapping.shot,
        project_data=query.project_data,
    )


@curry
def hierarchy_to_tasks_query(
    project: ShotgridProject,
    query: ShotgridHierarchyByProjectQuery,
) -> ShotgridFindTasksByProjectQuery:
    return ShotgridFindTasksByProjectQuery(
        project=project,
        credentials=query.credentials,
        task_mapping=query.fields_mapping.task,
        project_data=query.project_data,
    )


@curry
def hierarchy_to_linked_asset_to_asset_query(
    project: ShotgridProject,
    query: ShotgridHierarchyByProjectQuery,
) -> ShotgridLinkedEntitiesQuery:
    return ShotgridLinkedEntitiesQuery(
        project,
        query.credentials,
        query.fields_mapping.asset_to_asset,
    )


@curry
def hierarchy_to_linked_asset_to_shot_query(
    project: ShotgridProject,
    query: ShotgridHierarchyByProjectQuery,
) -> ShotgridLinkedEntitiesQuery:
    return ShotgridLinkedEntitiesQuery(
        project,
        query.credentials,
        query.fields_mapping.asset_to_shot,
    )


@curry
def hierarchy_to_linked_shot_to_shot_query(
    project: ShotgridProject,
    query: ShotgridHierarchyByProjectQuery,
) -> ShotgridLinkedEntitiesQuery:
    return ShotgridLinkedEntitiesQuery(
        project,
        query.credentials,
        query.fields_mapping.shot_to_shot,
    )
