from dataclasses import dataclass

from toolz import curry

from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials
from shotgrid_leecher.record.shotgrid_subtypes import (
    ShotgridProject,
    FieldsMapping,
    ProjectFieldMapping,
    AssetFieldMapping,
    ShotFieldMapping,
    TaskFieldMapping,
)


@dataclass(frozen=True)
class ShotgridBaseEntityQuery:
    project_id: int
    credentials: ShotgridCredentials


@dataclass(frozen=True)
class ShotgridHierarchyByProjectQuery:
    project_id: int
    credentials: ShotgridCredentials
    fields_mapping: FieldsMapping


@dataclass(frozen=True)
class ShotgridBoundEntityQuery:
    project: ShotgridProject
    credentials: ShotgridCredentials


@dataclass(frozen=True)
class ShotgridFindProjectByIdQuery(ShotgridBaseEntityQuery):
    project_mapping: ProjectFieldMapping

    @staticmethod
    def from_query(
        entity: ShotgridHierarchyByProjectQuery,
    ) -> "ShotgridFindProjectByIdQuery":
        return ShotgridFindProjectByIdQuery(
            entity.project_id,
            entity.credentials,
            entity.fields_mapping.project_mapping,
        )


@dataclass(frozen=True)
class ShotgridFindAssetsByProjectQuery(ShotgridBoundEntityQuery):
    asset_mapping: AssetFieldMapping

    @staticmethod
    @curry
    def from_query(
        project: ShotgridProject, query: ShotgridHierarchyByProjectQuery
    ) -> "ShotgridFindAssetsByProjectQuery":
        return ShotgridFindAssetsByProjectQuery(
            project,
            query.credentials,
            query.fields_mapping.asset_mapping,
        )


@dataclass(frozen=True)
class ShotgridFindShotsByProjectQuery(ShotgridBoundEntityQuery):
    shot_mapping: ShotFieldMapping

    @staticmethod
    @curry
    def from_query(
        project: ShotgridProject, query: ShotgridHierarchyByProjectQuery
    ) -> "ShotgridFindShotsByProjectQuery":
        return ShotgridFindShotsByProjectQuery(
            project,
            query.credentials,
            query.fields_mapping.shot_mapping,
        )


@dataclass(frozen=True)
class ShotgridFindTasksByProjectQuery(ShotgridBoundEntityQuery):
    task_mapping: TaskFieldMapping

    @staticmethod
    @curry
    def from_query(
        project: ShotgridProject, query: ShotgridHierarchyByProjectQuery
    ) -> "ShotgridFindTasksByProjectQuery":
        return ShotgridFindTasksByProjectQuery(
            project,
            query.credentials,
            query.fields_mapping.task_mapping,
        )
