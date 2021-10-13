from typing import Dict, Any

import attr
import cattr

from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials
from shotgrid_leecher.record.shotgrid_subtypes import FieldsMapping
from shotgrid_leecher.utils.strings import attr_value_to_dict


@attr.s(auto_attribs=True, frozen=True)
class ShotgridToAvalonBatchCommand:
    project_id: int
    project_name: str
    overwrite: bool
    credentials: ShotgridCredentials
    fields_mapping: FieldsMapping

    @staticmethod
    def from_dict(
        source: Dict[str, Any],
        overwrite: bool = False,
    ) -> "ShotgridToAvalonBatchCommand":
        params = {**source, "overwrite": overwrite}
        return cattr.structure(params, ShotgridToAvalonBatchCommand)


@attr.s(auto_attribs=True, frozen=True)
class ScheduleShotgridBatchCommand:
    project_id: int
    project_name: str
    credentials: ShotgridCredentials
    fields_mapping: FieldsMapping

    @staticmethod
    def from_dict(source: Dict[str, Any]) -> "ScheduleShotgridBatchCommand":
        return cattr.structure(source, ScheduleShotgridBatchCommand)

    def to_dict(self) -> Dict[str, Any]:
        return attr.asdict(self, value_serializer=attr_value_to_dict)


@attr.s(auto_attribs=True, frozen=True)
class ShotgridCheckCommand:
    project_name: str
    project_id: int
    credentials: ShotgridCredentials
