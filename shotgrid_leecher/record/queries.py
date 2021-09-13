from dataclasses import dataclass

from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials
from shotgrid_leecher.record.shotgrid_subtypes import ShotgridProject


@dataclass(frozen=True)
class ShotgridBaseEntityQuery:
    project_id: int
    credentials: ShotgridCredentials


@dataclass(frozen=True)
class ShotgridHierarchyByProjectQuery(ShotgridBaseEntityQuery):
    pass


@dataclass(frozen=True)
class ShotgridBoundEntityQuery:
    project: ShotgridProject
    credentials: ShotgridCredentials


@dataclass(frozen=True)
class ShotgridFindProjectByIdQuery(ShotgridBaseEntityQuery):
    @staticmethod
    def from_query(
        entity: ShotgridBaseEntityQuery,
    ) -> "ShotgridFindProjectByIdQuery":
        return ShotgridFindProjectByIdQuery(
            entity.project_id,
            entity.credentials,
        )


@dataclass(frozen=True)
class ShotgridFindAssetsByProjectQuery(ShotgridBoundEntityQuery):
    @staticmethod
    def from_query(
        project: ShotgridProject, query: ShotgridHierarchyByProjectQuery
    ) -> "ShotgridFindAssetsByProjectQuery":
        return ShotgridFindAssetsByProjectQuery(project, query.credentials)


@dataclass(frozen=True)
class ShotgridFindShotsByProjectQuery(ShotgridBoundEntityQuery):
    @staticmethod
    def from_query(
        project: ShotgridProject, query: ShotgridHierarchyByProjectQuery
    ) -> "ShotgridFindShotsByProjectQuery":
        return ShotgridFindShotsByProjectQuery(project, query.credentials)


@dataclass(frozen=True)
class ShotgridFindTasksByProjectQuery(ShotgridBoundEntityQuery):
    @staticmethod
    def from_query(
        project: ShotgridProject, query: ShotgridHierarchyByProjectQuery
    ) -> "ShotgridFindTasksByProjectQuery":
        return ShotgridFindTasksByProjectQuery(project, query.credentials)
