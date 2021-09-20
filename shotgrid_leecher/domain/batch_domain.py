from typing import Dict, Any, List, Iterator

from bson.objectid import ObjectId
from toolz import get_in

import shotgrid_leecher.mapper.hierarchy_mapper as mapper
import shotgrid_leecher.repository.shotgrid_entity_repo as entity_repo
import shotgrid_leecher.repository.shotgrid_hierarchy_repo as repository
from shotgrid_leecher.record.commands import (
    ShotgridToAvalonBatchCommand,
    ShotgridCheckCommand,
)
from shotgrid_leecher.record.queries import (
    ShotgridFindProjectByIdQuery,
    ShotgridHierarchyByProjectQuery,
)
from shotgrid_leecher.record.results import BatchCheckResult
from shotgrid_leecher.repository import hierarchy_repo
from shotgrid_leecher.writers import db_writer

Map = Dict[str, Any]


def _assign_object_ids(
    shotgrid_hierarchy: List[Map],
    last_hierarchy_rows: List[Map],
) -> Iterator[Map]:
    source_id_tree = {
        x["src_id"]: x for x in last_hierarchy_rows if x.get("src_id")
    }
    ids_tree = {
        x["_id"]: x for x in last_hierarchy_rows if not x.get("src_id")
    }
    for row in shotgrid_hierarchy:
        if row.get("src_id"):
            yield {
                **row,
                "object_id": source_id_tree.get(row["src_id"], dict()).get(
                    "object_id", ObjectId()
                ),
            }
            continue
        yield {
            **row,
            "object_id": ids_tree.get(row["_id"], dict()).get(
                "object_id", ObjectId()
            ),
        }


def _rearrange_parents(avalon_tree: Dict[str, Map], row: Map) -> Map:
    return {
        **row,
        "parent": (
            avalon_tree[row["parent"]]["_id"] if row.get("parent") else None
        ),
        "data": {
            **row["data"],
            "visualParent": (
                avalon_tree[row["data"]["visualParent"]].get("_id")
                if get_in("data.visualParent".split("."), row)
                else None
            ),
        },
    }


def check_shotgrid_before_batch(
    command: ShotgridCheckCommand,
) -> BatchCheckResult:
    project = entity_repo.find_project_by_id(
        ShotgridFindProjectByIdQuery(command.project_id, command.credentials)
    )
    status = "OK" if project else "KO"
    return BatchCheckResult(status)


def batch_shotgrid_to_avalon(command: ShotgridToAvalonBatchCommand):
    query = ShotgridHierarchyByProjectQuery(
        command.project_id,
        command.credentials,
    )
    hierarchy_rows = repository.get_hierarchy_by_project(query)
    avalon_tree = mapper.shotgrid_to_avalon(hierarchy_rows)

    if not avalon_tree:
        return

    avalon_rows = list(avalon_tree.values())

    for row in avalon_rows:
        object_id = db_writer.insert_avalon_row(
            command.project_name,
            _rearrange_parents(avalon_tree, row)
        )
        avalon_tree[row["name"]]["_id"] = object_id


def batch_update_shotgrid_to_avalon(command: ShotgridToAvalonBatchCommand):
    query = ShotgridHierarchyByProjectQuery(
        command.project_id,
        command.credentials,
    )
    hierarchy_rows = repository.get_hierarchy_by_project(query)
    if not hierarchy_rows:
        return
    last_hierarchy_rows = list(
        hierarchy_repo.get_last_rows(command.project_name)
    )
    hierarchy_rows = list(
        _assign_object_ids(hierarchy_rows, last_hierarchy_rows)
    )
    avalon_tree = mapper.shotgrid_to_avalon(hierarchy_rows)
    avalon_rows = list(avalon_tree.values())

    if command.overwrite:
        db_writer.drop_avalon_project(command.project_name)

    for row in avalon_rows:
        object_id = db_writer.upsert_avalon_row(
            command.project_name,
            _rearrange_parents(avalon_tree, row),
        )
        avalon_tree[row["name"]]["_id"] = object_id

    db_writer.overwrite_hierarchy(command.project_name, hierarchy_rows)
