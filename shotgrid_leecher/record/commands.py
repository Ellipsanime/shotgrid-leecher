from enum import Enum
from typing import Dict, Any

import attr

from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials
from shotgrid_leecher.record.shotgrid_subtypes import FieldsMapping


@attr.s(auto_attribs=True, frozen=True)
class ShotgridToAvalonBatchCommand:
    project_id: int
    project_name: str
    overwrite: bool
    credentials: ShotgridCredentials
    fields_mapping: FieldsMapping


@attr.s(auto_attribs=True, frozen=True)
class ScheduleShotgridBatchCommand:
    project_id: int
    project_name: str
    credentials: ShotgridCredentials
    fields_mapping: FieldsMapping

    def to_dict(self) -> Dict[str, Any]:
        def _serialize(type_: type, attribute: attr.Attribute, val: Any) -> Any:
            if isinstance(val, Enum):
                return val.value
            return val
        return attr.asdict(self, recurse=True, value_serializer=_serialize)


@attr.s(auto_attribs=True, frozen=True)
class ShotgridCheckCommand:
    project_name: str
    project_id: int
    credentials: ShotgridCredentials
