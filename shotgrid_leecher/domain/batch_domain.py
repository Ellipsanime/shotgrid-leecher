from typing import Dict, Any, List, Iterator, Set, Tuple, Optional

from bson.objectid import ObjectId
from toolz import get_in, curry, pipe

import shotgrid_leecher.repository.shotgrid_entity_repo as entity_repo
import shotgrid_leecher.repository.shotgrid_hierarchy_repo as repository
from shotgrid_leecher.mapper import avalon_mapper
from shotgrid_leecher.record.avalon_structures import AvalonProjectData
from shotgrid_leecher.record.commands import (
    UpdateShotgridInAvalonCommand,
    ShotgridCheckCommand,
    CreateShotgridInAvalonCommand,
)
from shotgrid_leecher.record.intermediate_structures import IntermediateRow
from shotgrid_leecher.record.queries import (
    ShotgridFindProjectByIdQuery,
    ShotgridHierarchyByProjectQuery,
)
from shotgrid_leecher.record.results import BatchCheckResult, BatchResult
from shotgrid_leecher.record.shotgrid_subtypes import ProjectFieldsMapping
from shotgrid_leecher.repository import (
    avalon_repo,
    intermediate_hierarchy_repo,
)
from shotgrid_leecher.utils import generator
from shotgrid_leecher.writers import db_writer

Map = Dict[str, Any]


def check_shotgrid_before_batch(
    command: ShotgridCheckCommand,
) -> BatchCheckResult:
    query = ShotgridFindProjectByIdQuery(
        command.project_id,
        command.credentials,
        AvalonProjectData(),
        ProjectFieldsMapping.from_dict({}),  # TODO make it differently
    )
    project = entity_repo.find_project_by_id(query)
    status = project.name if project else "KO"
    return BatchCheckResult(status)


def update_shotgrid_in_avalon(
    command: UpdateShotgridInAvalonCommand,
) -> BatchResult:
    shotgrid_hierarchy, dropped_ids = _fetch_and_augment_hierarchy(command)
    if not shotgrid_hierarchy:
        return BatchResult.NO_SHOTGRID_HIERARCHY
    # TODO get rid of mutability and avalon_tree
    avalon_tree = avalon_mapper.shotgrid_to_avalon(shotgrid_hierarchy)
    avalon_rows = list(avalon_tree.values())

    if command.project_name != avalon_rows[0]["name"]:
        return BatchResult.WRONG_PROJECT_NAME

    if command.overwrite:
        db_writer.drop_avalon_project(command.project_name)

    for row in avalon_rows:
        object_id = db_writer.upsert_avalon_row(
            command.project_name,
            _rearrange_parents(avalon_tree, row),
        )
        avalon_tree[row["name"]]["_id"] = object_id

    db_writer.delete_avalon_rows(command.project_name, dropped_ids)
    db_writer.overwrite_hierarchy(command.project_name, shotgrid_hierarchy)

    return BatchResult.OK


def create_shotgrid_in_avalon(command: CreateShotgridInAvalonCommand):
    default_project_data = AvalonProjectData()
    query = ShotgridHierarchyByProjectQuery(
        command.project_id,
        command.credentials,
        command.fields_mapping,
        default_project_data,
    )
    shotgrid_hierarchy = repository.get_hierarchy_by_project(query)
    # TODO get rid of mutability and avalon_tree
    avalon_tree = avalon_mapper.shotgrid_to_avalon(shotgrid_hierarchy)

    if not avalon_tree:
        return

    avalon_rows = list(avalon_tree.values())

    for row in avalon_rows:
        object_id = db_writer.insert_avalon_row(
            command.project_name, _rearrange_parents(avalon_tree, row)
        )
        avalon_tree[row["name"]]["_id"] = object_id


@curry
def _assign_object_ids(
    shotgrid_hierarchy: List[Map],
    intermediate_hierarchy: List[Map],
) -> Iterator[Map]:
    source_id_tree = {
        x["src_id"]: x for x in intermediate_hierarchy if x.get("src_id")
    }
    ids_tree = {
        x["_id"]: x for x in intermediate_hierarchy if not x.get("src_id")
    }
    for row in shotgrid_hierarchy:
        if row.get("src_id"):
            yield {
                **row,
                "object_id": source_id_tree.get(row["src_id"], dict()).get(
                    "object_id"
                )
                or generator.object_id(),
            }
            continue
        yield {
            **row,
            "object_id": ids_tree.get(row["_id"], dict()).get("object_id")
            or generator.object_id(),
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


@curry
def _fetch_intermediate_hierarchy(
    project_name: str, shotgrid_hierarchy: List[IntermediateRow]
) -> List[Map]:
    intermediate_hierarchy = list(
        intermediate_hierarchy_repo.fetch_by_project(project_name)
    )
    if intermediate_hierarchy:
        return intermediate_hierarchy
    avalon_project = avalon_mapper.entity_to_project(
        avalon_repo.fetch_project(project_name),
        shotgrid_hierarchy,
    )
    return [avalon_project] if avalon_project else []


def _to_paths(hierarchy: List[Map]) -> Set[Tuple[Optional[str], str]]:
    return {(x.get("parent"), x["_id"]) for x in hierarchy}


def _detect_deletion(
    shotgrid_hierarchy: List[Map],
    intermediate_hierarchy: List[Map],
) -> Set[Tuple[Optional[str], str]]:
    return _to_paths(intermediate_hierarchy) - _to_paths(shotgrid_hierarchy)


def _fetch_and_augment_hierarchy(
    command: UpdateShotgridInAvalonCommand,
) -> Tuple[List[Map], Set[ObjectId]]:
    query = ShotgridHierarchyByProjectQuery(
        command.project_id,
        command.credentials,
        command.fields_mapping,
        command.project_data,
    )
    shotgrid_hierarchy = repository.get_hierarchy_by_project(query)
    if not shotgrid_hierarchy:
        return [], set()
    intermediate_hierarchy, dropped_ids = pipe(
        shotgrid_hierarchy,
        _fetch_intermediate_hierarchy(command.project_name),
        _propagate_deletion(shotgrid_hierarchy),
    )
    return (
        list(_assign_object_ids(shotgrid_hierarchy, intermediate_hierarchy)),
        dropped_ids,
    )


@curry
def _propagate_deletion(
    shotgrid_hierarchy: List[Map],
    intermediate_hierarchy: List[Map],
) -> Tuple[List[Map], Set[ObjectId]]:
    deleted_ones = _detect_deletion(shotgrid_hierarchy, intermediate_hierarchy)
    if not deleted_ones:
        return intermediate_hierarchy, set()
    altered_hierarchy = [
        x
        for x in intermediate_hierarchy
        if not (x.get("parent"), x["_id"]) in deleted_ones
    ]
    deleted_object_ids = {
        x.get("object_id")
        for x in intermediate_hierarchy
        if (x.get("parent"), x["_id"]) in deleted_ones and x.get("object_id")
    }
    return altered_hierarchy, deleted_object_ids
