from typing import Any, Dict, Optional

import attr
from toolz import curry

from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials
from shotgrid_leecher.record.shotgrid_subtypes import (
    ShotgridProject,
    FieldsMapping,
    ProjectFieldsMapping,
    AssetFieldsMapping,
    ShotFieldsMapping,
    TaskFieldsMapping,
)


@attr.s(auto_attribs=True, frozen=True)
class FindEntityQuery:
    MAX_LIMIT = 25

    filter: Dict[str, Any] = dict()
    sort: Dict[str, Any] = dict()
    skip: Optional[int] = None
    limit: Optional[int] = None

    def skip_or_default(self) -> int:
        return self.skip or 0

    def limit_or_default(self) -> int:
        return min(
            FindEntityQuery.MAX_LIMIT, self.limit or FindEntityQuery.MAX_LIMIT
        )


@attr.s(auto_attribs=True, frozen=True)
class ShotgridBaseEntityQuery:
    project_id: int
    credentials: ShotgridCredentials


@attr.s(auto_attribs=True, frozen=True)
class ShotgridHierarchyByProjectQuery:
    project_id: int
    credentials: ShotgridCredentials
    fields_mapping: FieldsMapping


@attr.s(auto_attribs=True, frozen=True)
class ShotgridBoundEntityQuery:
    project: ShotgridProject
    credentials: ShotgridCredentials


@attr.s(auto_attribs=True, frozen=True)
class ShotgridFindProjectByIdQuery(ShotgridBaseEntityQuery):
    project_mapping: ProjectFieldsMapping

    @staticmethod
    def from_query(
        entity: ShotgridHierarchyByProjectQuery,
    ) -> "ShotgridFindProjectByIdQuery":
        return ShotgridFindProjectByIdQuery(
            entity.project_id,
            entity.credentials,
            entity.fields_mapping.project,
        )


@attr.s(auto_attribs=True, frozen=True)
class ShotgridFindAssetsByProjectQuery(ShotgridBoundEntityQuery):
    asset_mapping: AssetFieldsMapping
    task_mapping: TaskFieldsMapping

    @staticmethod
    @curry
    def from_query(
        project: ShotgridProject, query: ShotgridHierarchyByProjectQuery
    ) -> "ShotgridFindAssetsByProjectQuery":
        return ShotgridFindAssetsByProjectQuery(
            project,
            query.credentials,
            query.fields_mapping.asset,
            query.fields_mapping.task,
        )


@attr.s(auto_attribs=True, frozen=True)
class ShotgridFindShotsByProjectQuery(ShotgridBoundEntityQuery):
    shot_mapping: ShotFieldsMapping

    @staticmethod
    @curry
    def from_query(
        project: ShotgridProject, query: ShotgridHierarchyByProjectQuery
    ) -> "ShotgridFindShotsByProjectQuery":
        return ShotgridFindShotsByProjectQuery(
            project,
            query.credentials,
            query.fields_mapping.shot,
        )


@attr.s(auto_attribs=True, frozen=True)
class ShotgridFindTasksByProjectQuery(ShotgridBoundEntityQuery):
    task_mapping: TaskFieldsMapping

    @staticmethod
    @curry
    def from_query(
        project: ShotgridProject, query: ShotgridHierarchyByProjectQuery
    ) -> "ShotgridFindTasksByProjectQuery":
        return ShotgridFindTasksByProjectQuery(
            project,
            query.credentials,
            query.fields_mapping.task,
        )
