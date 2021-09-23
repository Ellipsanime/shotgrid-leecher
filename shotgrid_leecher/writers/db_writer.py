from typing import Dict, Any, List, Set

from bson import ObjectId
from pymongo.collection import Collection

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.enums import DbName
from shotgrid_leecher.utils.collections import flatten_dict

Map = Dict[str, Any]


def _avalon_collection(project_name: str) -> Collection:
    return (
        conn.get_db_client()
        .get_database(DbName.AVALON.value)
        .get_collection(project_name)
    )


def overwrite_hierarchy(project_name: str, hierarchy_rows: List[Map]):
    db = conn.get_db_client().get_database(DbName.INTERMEDIATE.value)
    db.drop_collection(project_name)
    db.get_collection(project_name).insert_many(hierarchy_rows)


def upsert_avalon_row(project_name: str, avalon_row: Map) -> ObjectId:
    query = {"$set": flatten_dict(avalon_row)}
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
