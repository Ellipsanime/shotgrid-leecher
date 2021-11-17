from typing import Dict, Any, List, Iterator, Set, Tuple, Optional, cast

import attr
from bson.objectid import ObjectId
from toolz import curry, pipe

import shotgrid_leecher.repository.shotgrid_entity_repo as entity_repo
import shotgrid_leecher.repository.shotgrid_hierarchy_repo as repository
from shotgrid_leecher.mapper import avalon_mapper, hierarchy_mapper
from shotgrid_leecher.record.avalon_structures import AvalonProjectData
from shotgrid_leecher.record.commands import (
    UpdateShotgridInAvalonCommand,
    ShotgridCheckCommand,
    CreateShotgridInAvalonCommand,
)
from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.record.intermediate_structures import (
    IntermediateRow,
    IntermediateShot,
)
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
from shotgrid_leecher.utils.functional import try_or, try_or_call
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
    current_hierarchy, dropped_ids = _fetch_and_augment_hierarchy(command)
    if not current_hierarchy:
        return BatchResult.NO_SHOTGRID_HIERARCHY
    # TODO get rid of mutability and avalon_tree
    avalon_tree = avalon_mapper.shotgrid_to_avalon(current_hierarchy)
    avalon_rows = list(avalon_tree.values())

    if command.project_name != avalon_rows[0]["name"]:
        return BatchResult.WRONG_PROJECT_NAME

    if command.overwrite:
        db_writer.drop_avalon_assets(command.project_name)

    for row in avalon_rows:
        object_id = db_writer.upsert_avalon_row(
            command.project_name,
            _rearrange_parents(avalon_tree, row),
        )
        avalon_tree[row["name"]]["_id"] = object_id

    db_writer.delete_avalon_rows(command.project_name, dropped_ids)
    db_writer.overwrite_hierarchy(command.project_name, current_hierarchy)

    return BatchResult.OK


def create_shotgrid_in_avalon(command: CreateShotgridInAvalonCommand):
    default_project_data = AvalonProjectData()
    query = ShotgridHierarchyByProjectQuery(
        command.project_id,
        command.credentials,
        command.fields_mapping,
        default_project_data,
    )
    current_hierarchy = repository.get_hierarchy_by_project(query)
    # TODO get rid of mutability and avalon_tree
    avalon_tree = avalon_mapper.shotgrid_to_avalon(current_hierarchy)

    if not avalon_tree:
        return

    avalon_rows = list(avalon_tree.values())

    for row in avalon_rows:
        object_id = db_writer.insert_avalon_row(
            command.project_name, _rearrange_parents(avalon_tree, row)
        )
        avalon_tree[row["name"]]["_id"] = object_id


def _assign_linked_assets_ids(
    rows: List[IntermediateRow],
) -> Iterator[IntermediateRow]:
    ids_hash = {
        x.src_id: x.object_id for x in rows if x.type == ShotgridType.ASSET
    }
    with_ = attr.evolve
    for row in rows:
        if row.type != ShotgridType.SHOT:
            yield row
            continue
        shot = cast(IntermediateShot, row)
        linked_assets = [
            with_(x, object_id=ids_hash[x.id])
            for x in shot.linked_assets
            if ids_hash.get(x.id)
        ]
        yield with_(shot, linked_assets=linked_assets)


@curry
def _assign_object_ids(
    current_hierarchy: List[IntermediateRow],
    previous_hierarchy: List[IntermediateRow],
) -> Iterator[IntermediateRow]:
    src_ids_hash, ids_hash = _get_hashes(previous_hierarchy)
    for row in current_hierarchy:
        if row.has_field("src_id") and row.src_id:
            src_id = cast(int, row.src_id)
            object_id = try_or_call(
                lambda: src_ids_hash[src_id].object_id,
                lambda: generator.object_id(),
            )
            yield attr.evolve(row, object_id=object_id)
            continue

        object_id = try_or_call(
            lambda: ids_hash[row.id].object_id,
            lambda: generator.object_id(),
        )
        yield attr.evolve(row, object_id=object_id)


def _get_hashes(
    previous_hierarchy: List[IntermediateRow],
) -> Tuple[Dict[int, IntermediateRow], Dict[str, IntermediateRow]]:
    src_ids_hash = {
        x.src_id: x
        for x in previous_hierarchy
        if x.has_field("src_id") and x.src_id
    }
    ids_hash = {x.id: x for x in previous_hierarchy if not x.src_id}
    return src_ids_hash, ids_hash


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
                if (row.get("data") or dict()).get("visualParent")
                else None
            ),
        },
    }


@curry
def _fetch_previous_hierarchy(
    project_name: str,
    project_data: AvalonProjectData,
    current_hierarchy: List[IntermediateRow],
) -> List[IntermediateRow]:
    project_params = hierarchy_mapper.to_params(project_data)
    previous_hierarchy = list(
        intermediate_hierarchy_repo.fetch_by_project(
            project_name, project_params
        )
    )
    if previous_hierarchy:
        return previous_hierarchy
    avalon_project = avalon_mapper.entity_to_project(
        avalon_repo.fetch_project(project_name),
        current_hierarchy,
    )
    return [avalon_project] if avalon_project else []


def _to_paths(
    hierarchy: List[IntermediateRow],
) -> Set[Tuple[Optional[str], str]]:
    return {(try_or(lambda: x.parent), x.id) for x in hierarchy}


def _detect_deletion(
    current_hierarchy: List[IntermediateRow],
    previous_hierarchy: List[IntermediateRow],
) -> Set[Tuple[Optional[str], str]]:
    return _to_paths(previous_hierarchy) - _to_paths(current_hierarchy)


def _fetch_and_augment_hierarchy(
    command: UpdateShotgridInAvalonCommand,
) -> Tuple[List[IntermediateRow], Set[ObjectId]]:
    query = ShotgridHierarchyByProjectQuery(
        command.project_id,
        command.credentials,
        command.fields_mapping,
        command.project_data,
    )
    current_hierarchy = repository.get_hierarchy_by_project(query)
    if not current_hierarchy:
        return [], set()
    previous_hierarchy, dropped_ids = pipe(
        current_hierarchy,
        _fetch_previous_hierarchy(command.project_name, command.project_data),
        _propagate_deletion(current_hierarchy),
    )
    assigned_hierarchy = list(
        _assign_object_ids(current_hierarchy, previous_hierarchy)
    )
    return (
        list(_assign_linked_assets_ids(assigned_hierarchy)),
        dropped_ids,
    )


@curry
def _propagate_deletion(
    current_hierarchy: List[IntermediateRow],
    previous_hierarchy: List[IntermediateRow],
) -> Tuple[List[IntermediateRow], Set[ObjectId]]:
    deleted_ones = _detect_deletion(current_hierarchy, previous_hierarchy)
    if not deleted_ones:
        return previous_hierarchy, set()
    altered_hierarchy = [
        x for x in previous_hierarchy if not (x.parent, x.id) in deleted_ones
    ]
    deleted_object_ids = {
        x.object_id
        for x in previous_hierarchy
        if (x.parent, x.id) in deleted_ones and x.object_id
    }
    return altered_hierarchy, deleted_object_ids
