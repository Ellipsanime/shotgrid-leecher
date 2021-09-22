from typing import Dict, Any, List

from bson import ObjectId

import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.utils.collections import flatten_dict

Map = Dict[str, Any]


def overwrite_hierarchy(project_name: str, hierarchy_rows: List[Map]):
    db = conn.get_db_client().get_database("shotgrid_openpype")
    db.drop_collection(project_name)
    db.get_collection(project_name).insert_many(hierarchy_rows)


def upsert_avalon_row(project_name: str, avalon_row: Map) -> ObjectId:
    db = conn.get_db_client().get_database("avalon")
    col = db.get_collection(project_name)
    query = {"$set": flatten_dict(avalon_row)}
    res = col.update_one({"_id": avalon_row["_id"]}, query, upsert=True)
    if res.upserted_id:
        return res.upserted_id
    return avalon_row["_id"]


def insert_avalon_row(project_name: str, avalon_row: Map) -> ObjectId:
    collection = (
        conn.get_db_client()
        .get_database("avalon")
        .get_collection(project_name)
    )
    return collection.insert_one(avalon_row).inserted_id


def drop_avalon_project(project_name: str):
    db = conn.get_db_client().get_database("avalon")
    db.drop_collection(project_name)
    db.create_collection(project_name)
