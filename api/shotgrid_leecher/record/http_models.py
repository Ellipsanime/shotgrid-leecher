from typing import Optional, Dict, Any

import validators
from pydantic import BaseModel, Field, validator
from pydantic.fields import ModelField
from pydantic.main import ModelMetaclass


def _validate_shotgrid_url(url: str) -> str:
    if not validators.url(url):
        raise ValueError(f"shotgrid_url {url} should be a valid url")
    return url


def _validate_non_empty_fields(*args) -> Any:
    value, _, _, field = args
    if value is None:
        raise ValueError(f'Model field "{field.name}" can be null')
    return value


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


class ShotgridUrlModel(BaseModel):
    shotgrid_url: str = Field(None, title="Shotgrid server url")

    @validator("shotgrid_url")
    def validate_shotgrid_url(cls: ModelMetaclass, url: str) -> str:
        return _validate_shotgrid_url(url)

    @validator("*", pre=True, always=True)
    def validate_non_empty_fields(
        cls: ModelMetaclass,
        value: Optional[Any],
        values: Any,
        config: Dict,
        field: ModelField,
    ) -> Any:
        return _validate_non_empty_fields(value, values, config, field)


class ShotgridCredentialsModel(BaseModel):
    shotgrid_url: str = Field(None, title="Shotgrid server url")
    script_name: str = Field(None, title="Shotgrid script name")
    script_key: str = Field(None, title="Shotgrid script key")

    @validator("shotgrid_url")
    def validate_shotgrid_url(cls: ModelMetaclass, url: str) -> str:
        return _validate_shotgrid_url(url)

    @validator("*", pre=True, always=True)
    def validate_non_empty_fields(
        cls: ModelMetaclass,
        value: Optional[Any],
        values: Any,
        config: Dict,
        field: ModelField,
    ) -> Any:
        return _validate_non_empty_fields(value, values, config, field)


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
    def validate_shotgrid_url(cls: ModelMetaclass, url: str) -> str:
        return _validate_shotgrid_url(url)

    @validator("*", pre=True, always=True)
    def validate_non_empty_fields(
        cls: ModelMetaclass,
        value: Optional[Any],
        values: Any,
        config: Dict,
        field: ModelField,
    ) -> Any:
        return _validate_non_empty_fields(value, values, config, field)

