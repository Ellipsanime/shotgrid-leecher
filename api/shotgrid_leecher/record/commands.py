from datetime import datetime as dt
from typing import Dict, Any, List

import attr
import cattr

from shotgrid_leecher.record.avalon_structures import AvalonProjectData
from shotgrid_leecher.record.http_models import BatchConfig
from shotgrid_leecher.record.leecher_structures import ShotgridCredentials
from shotgrid_leecher.record.results import BatchResult, LogType
from shotgrid_leecher.record.shotgrid_structures import ShotgridProjectUserLink
from shotgrid_leecher.record.shotgrid_subtypes import FieldsMapping
from shotgrid_leecher.utils.strings import attr_value_to_dict


@attr.s(auto_attribs=True, frozen=True)
class UpsertProjectUserLinksCommand:
    links: List[ShotgridProjectUserLink]


@attr.s(auto_attribs=True, frozen=True)
class CancelBatchSchedulingCommand:
    project_name: str


@attr.s(auto_attribs=True, frozen=True)
class UpsertShotgridCredentialsCommand:
    credentials: ShotgridCredentials


@attr.s(auto_attribs=True, frozen=True)
class DeleteShotgridCredentialsCommand:
    shotgrid_url: str


@attr.s(auto_attribs=True, frozen=True)
class CreateShotgridInAvalonCommand:
    project_id: int
    project_name: str
    credentials: ShotgridCredentials
    fields_mapping: FieldsMapping

    @staticmethod
    def from_dict(
        source: Dict[str, Any],
        overwrite: bool = False,
    ) -> "CreateShotgridInAvalonCommand":
        params = {**source, "overwrite": overwrite}
        return cattr.structure(params, CreateShotgridInAvalonCommand)

    @staticmethod
    def from_http_model(
        project_name: str,
        model: BatchConfig,
    ) -> "CreateShotgridInAvalonCommand":
        credentials = ShotgridCredentials.from_dict(model.dict())
        return CreateShotgridInAvalonCommand(
            model.shotgrid_project_id,
            project_name,
            credentials,
            FieldsMapping.from_dict(model.fields_mapping),
        )


@attr.s(auto_attribs=True, frozen=True)
class UpdateShotgridInAvalonCommand:
    project_id: int
    project_name: str
    overwrite: bool
    credentials: ShotgridCredentials
    fields_mapping: FieldsMapping
    project_data: AvalonProjectData

    @staticmethod
    def from_dict(
        source: Dict[str, Any],
        overwrite: bool = False,
    ) -> "UpdateShotgridInAvalonCommand":
        params = {**source, "overwrite": overwrite}
        return cattr.structure(params, UpdateShotgridInAvalonCommand)

    @staticmethod
    def from_http_model(
        project_name: str,
        model: BatchConfig,
        project_data: AvalonProjectData,
    ) -> "UpdateShotgridInAvalonCommand":
        credentials = ShotgridCredentials.from_dict(model.dict())
        return UpdateShotgridInAvalonCommand(
            model.shotgrid_project_id,
            project_name,
            model.overwrite,
            credentials,
            FieldsMapping.from_dict(model.fields_mapping),
            project_data,
        )


@attr.s(auto_attribs=True, frozen=True)
class CleanScheduleBatchLogsCommand:
    datetime_gt: dt


@attr.s(auto_attribs=True, frozen=True)
class ScheduleShotgridBatchCommand:
    project_id: int
    project_name: str
    credentials: ShotgridCredentials
    fields_mapping: FieldsMapping

    @staticmethod
    def from_http_model(
        project_name: str,
        model: BatchConfig,
    ) -> "ScheduleShotgridBatchCommand":
        credentials = ShotgridCredentials.from_dict(model.dict())
        return ScheduleShotgridBatchCommand(
            model.shotgrid_project_id,
            project_name,
            credentials,
            FieldsMapping.from_dict(model.fields_mapping),
        )

    @staticmethod
    def from_dict(source: Dict[str, Any]) -> "ScheduleShotgridBatchCommand":
        return cattr.structure(source, ScheduleShotgridBatchCommand)

    def to_dict(self) -> Dict[str, Any]:
        return attr.asdict(self, value_serializer=attr_value_to_dict)


@attr.s(auto_attribs=True, frozen=True)
class ShotgridCheckCommand:
    project_id: int
    credentials: ShotgridCredentials


@attr.s(auto_attribs=True, frozen=True)
class BaseLogCommand:
    project_name: str
    project_id: int
    duration: float
    data: Any
    datetime: dt


@attr.s(auto_attribs=True, frozen=True)
class LogScheduleUpdateCommand(BaseLogCommand):
    batch_result: BatchResult
    type: LogType = LogType.SCHEDULE

    def to_dict(self) -> Dict[str, Any]:
        return attr.asdict(self, value_serializer=attr_value_to_dict)
