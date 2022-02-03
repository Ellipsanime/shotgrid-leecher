from typing import Optional, Dict, Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, validator
from pydantic.fields import ModelField
from pydantic.main import ModelMetaclass


class ScheduleQueryParams(BaseModel):
    filter_field: Optional[str] = Field(None, title="Filter field name")
    filter_value: Optional[str] = Field(None, title="Filter value")
    filter_value_type: Optional[str] = Field(None, title="Filter value")
    sort_field: Optional[str] = Field(None, title="Sort-by field value")
    sort_order: Optional[int] = Field(None, title="Sort-by order (1/-1)")
    skip: Optional[int] = Field(None, title="Count of rows to be skipped")
    limit: Optional[int] = Field(
        None, title="Amount of rows to return(max: 25)"
    )


class BatchConfig(BaseModel):
    shotgrid_url: str = Field(None, title="Shotgrid server url")
    shotgrid_project_id: int = Field(None, title="Shotgrid project id")
    script_name: str = Field(None, title="Shotgrid script name")
    script_key: str = Field(None, title="Shotgrid script key")
    overwrite: bool = Field(
        default=False,
        title="Flag that specifies whether batch "
        "should overwrite existing data or not",
    )
    fields_mapping: Dict[str, Dict[str, str]]

    @validator("shotgrid_url")
    def validate_shotgrid_url(cls, url: str) -> str:
        if not urlparse(url):
            raise ValueError(f"shotgrid_url {url} should be a valid url")
        return url

    @validator("*", pre=True, always=True)
    def validate_non_empty_fields(
        cls: ModelMetaclass,
        value: Optional[Any],
        values: Any,
        config: Dict,
        field: ModelField,
    ) -> Any:
        if value is None:
            raise ValueError(f'Model field "{field.name}" can be null')
        return value
