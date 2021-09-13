from dataclasses import dataclass

from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials


@dataclass(frozen=True)
class ShotgridToAvalonBatchCommand:
    project_id: int
    project_name: str
    overwrite: bool
    credentials: ShotgridCredentials
