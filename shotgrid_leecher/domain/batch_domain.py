from typing import Dict, List, Any

from pymongo import MongoClient
from bson.objectid import ObjectId

import shotgrid_leecher.mapper.hierarchy_mapper as mapper
import shotgrid_leecher.repository.shotgrid_entity_repo as entity_repo
import shotgrid_leecher.repository.shotgrid_hierarchy_repo as repository
import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.commands import (
    ShotgridToAvalonBatchCommand,
    ShotgridCheckCommand,
)
from shotgrid_leecher.record.queries import (
    ShotgridFindProjectByIdQuery,
    ShotgridHierarchyByProjectQuery,
)
from shotgrid_leecher.record.results import BatchCheckResult

Map = Dict[str, Any]


def check_shotgrid_before_batch(
    command: ShotgridCheckCommand,
) -> BatchCheckResult:
    project = entity_repo.find_project_by_id(
        ShotgridFindProjectByIdQuery(command.project_id, command.credentials)
    )
    status = "OK" if project else "KO"
    return BatchCheckResult(status)


def batch_shotgrid_to_avalon(command: ShotgridToAvalonBatchCommand):
    mongo_client: MongoClient = conn.get_db_client()
    query = ShotgridHierarchyByProjectQuery(
        command.project_id,
        command.credentials,
    )
    intermediate_rows = repository.get_hierarchy_by_project(query)
    mapped_rows = mapper.shotgrid_to_avalon(intermediate_rows)

    if not mapped_rows:
        return

    # list_mapped_rows = hierarchy_map_to_ordered_list(mapped_rows)
    list_mapped_rows = list(mapped_rows.values())

    db = mongo_client.get_database("avalon")
    # if collection exist
    #  - remove collection
    col = db.get_collection(intermediate_rows[0]["_id"])

    for row in list_mapped_rows:

        if "parent" in row and row["parent"]:
            row["parent"] = mapped_rows[row["parent"]]["_id"]

        if "visualParent" in row["data"] and row["data"]["visualParent"]:
            row["data"]["visualParent"] = mapped_rows[
                row["data"]["visualParent"]
            ]["_id"]

        oid = col.insert_one(row).inserted_id
        mapped_rows[row["name"]]["_id"] = oid


def add_oids(intermediate_rows, last_intermediate_rows):

    src_mapped_last_intermediate_rows = {
        x["src_id"]: x for x in last_intermediate_rows if x.get("src_id")
    }
    id_mapped_last_intermediate_rows = {
        x["_id"]: x for x in last_intermediate_rows if not x.get("src_id")
    }

    for row in intermediate_rows:

        if row.get("src_id"):
            if src_mapped_last_intermediate_rows.get(row["src_id"]):
                row["oid"] = src_mapped_last_intermediate_rows[row["src_id"]][
                    "oid"
                ]
            else:
                row["oid"] = ObjectId()
        else:
            if id_mapped_last_intermediate_rows.get(row["_id"]):
                row["oid"] = id_mapped_last_intermediate_rows[row["_id"]][
                    "oid"
                ]
            else:
                row["oid"] = ObjectId()

    return intermediate_rows


class InsertMongoAvalon:

    client: MongoClient

    def __init__(self, client: MongoClient):
        self.client = client

    def get_last_intermediate_rows(self, project_name: str):
        so_db = self.client.get_database("shotgrid_openpype")
        return so_db.get_collection(project_name).find({})

    def insert_intermediate_rows(
        self, project_name: str, intermediate_rows: List[Map]
    ):
        so_db = self.client.get_database("shotgrid_openpype")
        so_db.drop_collection(project_name)
        so_db.get_collection(project_name).insert_many(intermediate_rows)

    def upsert_in_avalon(self, project_name: str, row: Map) -> ObjectId:
        db = self.client.get_database("avalon")
        col = db.get_collection(project_name)
        query = {"$set": row}
        return col.update_one(
            {"_id": row["_id"]}, query, upsert=True
        ).upserted_id


def batch_update_shotgrid_to_avalon(command: ShotgridToAvalonBatchCommand):
    mongo_inserter = InsertMongoAvalon(conn.get_db_client())
    intermediate_rows = repository.get_hierarchy_by_project(command.project_id)

    if not intermediate_rows:
        return

    project_name = intermediate_rows[0]["_id"]

    last_intermediate_rows = mongo_inserter.get_last_intermediate_rows(
        project_name
    )
    intermediate_rows = add_oids(intermediate_rows, last_intermediate_rows)

    mongo_inserter.insert_intermediate_rows(project_name, intermediate_rows)

    mapped_rows = mapper.shotgrid_to_avalon(intermediate_rows)

    # list_mapped_rows = hierarchy_map_to_ordered_list(mapped_rows)
    list_mapped_rows = list(mapped_rows.values())

    for row in list_mapped_rows:

        if "parent" in row and row["parent"]:
            row["parent"] = mapped_rows[row["parent"]]["_id"]

        if "visualParent" in row["data"] and row["data"]["visualParent"]:
            row["data"]["visualParent"] = mapped_rows[
                row["data"]["visualParent"]
            ]["_id"]

        oid = mongo_inserter.upsert_in_avalon(project_name, row)
        mapped_rows[row["name"]]["_id"] = oid
