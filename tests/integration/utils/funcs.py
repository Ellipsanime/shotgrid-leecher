import uuid
from typing import Any, List, Union, Dict, Callable

from mongomock.object_id import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from toolz import curry

from shotgrid_leecher.record.avalon_structures import (
    AvalonProject,
    AvalonProjectData,
)
from shotgrid_leecher.record.enums import ShotgridType, DbName
from shotgrid_leecher.record.http_models import BatchConfig

Map = Dict[str, Any]


@curry
def sg_query(
    data: Any,
    type_: str,
    filters: List[List[Any]],
    fields: List[str],
) -> Union[List[Map], Map]:
    if type_ == ShotgridType.PROJECT.value:
        return data.SHOTGRID_DATA_PROJECT[0]
    if type_ == ShotgridType.ASSET.value:
        return data.SHOTGRID_DATA_ASSETS
    if type_ == ShotgridType.SHOT.value:
        return data.SHOTGRID_DATA_SHOTS
    if type_ == ShotgridType.TASK.value:
        return data.SHOTGRID_DATA_TASKS
    raise RuntimeError(f"Unknown type {type_}")


def batch_config(overwrite=True) -> BatchConfig:
    return BatchConfig(
        shotgrid_project_id=123,
        overwrite=overwrite,
        shotgrid_url="http://google.com",
        script_name="1",
        script_key="1",
        fields_mapping={},
    )


def avalon_collections(client: MongoClient) -> List[str]:
    return client.get_database(DbName.AVALON.value).list_collection_names()


def intermediate_collections(client: MongoClient) -> List[str]:
    return client.get_database(
        DbName.INTERMEDIATE.value
    ).list_collection_names()


def all_avalon(client: MongoClient) -> List[Map]:
    col = client.get_database(DbName.AVALON.value).list_collection_names()[0]
    return list(
        client.get_database(DbName.AVALON.value).get_collection(col).find({})
    )


def all_intermediate(client: MongoClient) -> List[Map]:
    col = client.get_database(
        DbName.INTERMEDIATE.value
    ).list_collection_names()[0]
    return list(
        client.get_database(DbName.INTERMEDIATE.value)
        .get_collection(col)
        .find({})
    )


def populate_db(db: Collection, data: List[Map]) -> None:
    db.delete_many({})
    db.insert_many(data)


def fun(param: Any) -> Callable[[Any], Any]:
    return lambda *_: param


def get_project(name: str) -> AvalonProject:
    return AvalonProject(
        id=str(ObjectId()),
        name=name,
        data=AvalonProjectData(tools_env=[str(uuid.uuid4())]),
        config=dict(),
    )
