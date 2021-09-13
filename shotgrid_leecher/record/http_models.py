from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

from shotgrid_leecher.record.commands import ShotgridToAvalonBatchCommand
from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials


class BatchConfig(BaseModel):
    shotgrid_url: str = Field(None, title="Shotgrid server url")
    shotgrid_project_id: int = Field(None, title="Shotgrid project id")
    script_name: str = Field(None, title="Shotgrid script name")
    script_key: str = Field(None, title="Shotgrid script key")
    overwrite: bool = Field(
        None,
        title="Flag that specifies whether batch "
              "should overwrite existing data or not",
    )
    fields_mapping: Optional[Dict[str, Any]]

    def to_batch_command(
        self,
        project_name: str,
        overwrite: bool,
    ) -> ShotgridToAvalonBatchCommand:
        credentials = ShotgridCredentials(
            self.shotgrid_url,
            self.script_name,
            self.script_key,
        )
        return ShotgridToAvalonBatchCommand(
            self.shotgrid_project_id,
            project_name,
            overwrite,
            credentials,
        )
