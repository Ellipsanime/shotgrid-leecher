from typing import Dict, Any, List, Set

from bson import ObjectId
from pymongo.collection import Collection
from pymongo.results import DeleteResult

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.enums import DbName, AvalonType
from shotgrid_leecher.record.intermediate_structures import IntermediateRow
from shotgrid_leecher.utils.collections import flatten_dict

Map = Dict[str, Any]
_ROW_FLATTEN_EXCEPTIONS = {"config.tasks", "data.tasks"}


def _avalon_collection(project_name: str) -> Collection:
    return (
        conn.get_db_client()
        .get_database(DbName.AVALON.value)
        .get_collection(project_name)
    )


def _hierarchy_collection(project_name: str) -> Collection:
    return (
        conn.get_db_client()
        .get_database(DbName.INTERMEDIATE.value)
        .get_collection(project_name)
    )


def overwrite_hierarchy(
    project_name: str,
    hierarchy_rows: List[IntermediateRow],
) -> None:
    db = conn.get_db_client().get_database(DbName.INTERMEDIATE.value)
    db.drop_collection(project_name)
    db.get_collection(project_name).insert_many(
        [x.to_dict() for x in hierarchy_rows]
    )


def upsert_avalon_row(project_name: str, avalon_row: Map) -> ObjectId:
    query = {"$set": flatten_dict(avalon_row, _ROW_FLATTEN_EXCEPTIONS)}
    result = _avalon_collection(project_name).update_one(
        {"_id": avalon_row["_id"]}, query, upsert=True
    )
    if result.upserted_id:
        return result.upserted_id
    return avalon_row["_id"]


def delete_avalon_rows(project_name: str, ids: Set[ObjectId]) -> int:
    return (
        _avalon_collection(project_name)
        .delete_many({"_id": {"$in": list(ids)}})
        .deleted_count
    )


def insert_avalon_row(project_name: str, avalon_row: Map) -> ObjectId:
    return _avalon_collection(project_name).insert_one(avalon_row).inserted_id


def drop_avalon_project(project_name: str):
    db = conn.get_db_client().get_database(DbName.AVALON.value)
    db.drop_collection(project_name)
    db.create_collection(project_name)


def drop_avalon_assets(project_name: str) -> DeleteResult:
    db = (
        conn.get_db_client()
        .get_database(DbName.AVALON.value)
        .get_collection(project_name)
    )
    return db.delete_many({"type": {"$eq": AvalonType.ASSET.value}})


def rename_project_collections(
    project_name: str, new_project_name: str, overwrite: bool = False
):
    _avalon_collection(project_name).rename(
        new_project_name, dropTarget=overwrite
    )
    _hierarchy_collection(project_name).rename(
        new_project_name, dropTarget=overwrite
    )
