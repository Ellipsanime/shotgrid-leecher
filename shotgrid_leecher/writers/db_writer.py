from typing import Dict, Any, List

from bson import ObjectId

import shotgrid_leecher.utils.connectivity as conn

Map = Dict[str, Any]


def overwrite_hierarchy(project_name: str, hierarchy_rows: List[Map]):
    db = conn.get_db_client().get_database("shotgrid_openpype")
    db.drop_collection(project_name)
    db.get_collection(project_name).insert_many(hierarchy_rows)


def upsert_avalon_row(project_name: str, avalon_row: Map) -> ObjectId:
    db = conn.get_db_client().get_database("avalon")
    col = db.get_collection(project_name)
    query = {"$set": avalon_row}
    return col.update_one(
        {"_id": avalon_row["_id"]}, query, upsert=True
    ).upserted_id
