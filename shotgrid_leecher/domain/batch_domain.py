from typing import Dict, Any

from pymongo import MongoClient

import shotgrid_leecher.mapper.hierarchy_mapper as mapper
import shotgrid_leecher.repository.shotgrid_entity_repo as entity_repo
import shotgrid_leecher.repository.shotgrid_hierarchy_repo as repository
import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.commands import ShotgridToAvalonBatchCommand, \
    ShotgridCheckCommand
from shotgrid_leecher.record.queries import (
    ShotgridFindProjectByIdQuery,
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
    intermediate_rows = repository.get_hierarchy_by_project(command.project_id)
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
