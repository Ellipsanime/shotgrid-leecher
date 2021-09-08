from typing import Dict, List, Any
from pymongo import MongoClient

from shotgrid_leecher.utils.connectivity import (
    ShotgridClient,
    get_shotgrid_client,
    get_db_client,
)
from dataclasses import dataclass
import shotgrid_leecher.repository.shotgrid_hierarchy_repo as repository
import shotgrid_leecher.mapper.hierarchy_mapper as mapper

Map = Dict[str, Any]


@dataclass(frozen=True)
class ShotgridToAvalonBatchCommand:
    project_id: int
    overwrite: bool = False


def hierarchy_map_to_ordered_list(dic: Dict[str, Map]) -> List[Map]:
    pass


def shotgrid_to_avalon(command: ShotgridToAvalonBatchCommand):
    mongo_client: MongoClient = get_db_client()
    sg_client = ShotgridClient(get_shotgrid_client())
    intermediate_rows = repository.get_hierarchy_by_project(
        command.project_id, sg_client
    )
    mapped_rows = mapper.shotgrid_to_avalon(intermediate_rows)
    list_mapped_rows = hierarchy_map_to_ordered_list(mapped_rows)

    db = mongo_client["avalon"]
    # if collection exist
    #  - remove collection
    col = db[intermediate_rows[0]["_id"]]

    for row in list_mapped_rows:

        if "parent" in row and row["parent"]:
            row["parent"] = mapped_rows[row["parent"]]["_id"]

        if "visualParent" in row["data"] and row["data"]["visualParent"]:
            row["visualParent"] = mapped_rows[row["visualParent"]]["_id"]

        oid = col.insert_one(row).inserted_id
        mapped_rows[row["name"]]["_id"] = oid
