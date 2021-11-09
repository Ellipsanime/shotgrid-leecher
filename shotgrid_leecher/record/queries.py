from typing import Any, Dict, Optional, List, Tuple

import attr

from shotgrid_leecher.record.avalon_structures import AvalonProjectData
from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials
from shotgrid_leecher.record.shotgrid_subtypes import (
    ShotgridProject,
    FieldsMapping,
    ProjectFieldsMapping,
    AssetFieldsMapping,
    ShotFieldsMapping,
    TaskFieldsMapping,
    StepFieldsMapping,
)


@attr.s(auto_attribs=True, frozen=True)
class FindEntityQuery:
    _MAX_LIMIT = 25

    filter: Dict[str, Any] = dict()
    sort: List[Tuple[str, Any]] = []
    skip: Optional[int] = None
    limit: Optional[int] = None

    def skip_or_default(self) -> int:
        return self.skip or 0

    def limit_or_default(self) -> int:
        return min(
            FindEntityQuery._MAX_LIMIT,
            self.limit or FindEntityQuery._MAX_LIMIT,
        )


@attr.s(auto_attribs=True, frozen=True)
class ShotgridBaseEntityQuery:
    project_id: int
    credentials: ShotgridCredentials
    project_data: AvalonProjectData


@attr.s(auto_attribs=True, frozen=True)
class ShotgridHierarchyByProjectQuery:
    project_id: int
    credentials: ShotgridCredentials
    fields_mapping: FieldsMapping
    project_data: AvalonProjectData


@attr.s(auto_attribs=True, frozen=True)
class ShotgridBoundEntityQuery:
    project: ShotgridProject
    credentials: ShotgridCredentials
    project_data: AvalonProjectData


@attr.s(auto_attribs=True, frozen=True)
class ShotgridFindProjectByIdQuery(ShotgridBaseEntityQuery):
    project_mapping: ProjectFieldsMapping


@attr.s(auto_attribs=True, frozen=True)
class ShotgridFindAssetsByProjectQuery(ShotgridBoundEntityQuery):
    asset_mapping: AssetFieldsMapping
    task_mapping: TaskFieldsMapping


@attr.s(auto_attribs=True, frozen=True)
class ShotgridFindShotsByProjectQuery(ShotgridBoundEntityQuery):
    shot_mapping: ShotFieldsMapping


@attr.s(auto_attribs=True, frozen=True)
class ShotgridFindTasksByProjectQuery(ShotgridBoundEntityQuery):
    task_mapping: TaskFieldsMapping


@attr.s(auto_attribs=True, frozen=True)
class ShotgridFindAllStepsQuery(ShotgridBoundEntityQuery):
    step_mapping: StepFieldsMapping
