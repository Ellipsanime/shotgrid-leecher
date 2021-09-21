from itertools import chain, starmap
from typing import Dict, Any, List, Tuple, Iterable

from bson import ObjectId

import shotgrid_leecher.utils.connectivity as conn

Map = Dict[str, Any]


def overwrite_hierarchy(project_name: str, hierarchy_rows: List[Map]):
    db = conn.get_db_client().get_database("shotgrid_openpype")
    db.drop_collection(project_name)
    db.get_collection(project_name).insert_many(hierarchy_rows)


def _unpack_nested(
    key: str, value: Any, sep: str = "."
) -> Iterable[Tuple[str, Any]]:
    value_type = type(value)
    if value_type is dict:
        if not value:
            yield key, None
        for k, v in value.items():
            yield key + sep + k, v
    if value_type is not dict:
        yield key, value


def flatten_dict(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    dict_ = dictionary
    while True:
        dict_ = dict(
            chain.from_iterable(starmap(_unpack_nested, dict_.items()))
        )
        if not any(type(x) is dict for x in dict_.values()):
            return dict_


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
