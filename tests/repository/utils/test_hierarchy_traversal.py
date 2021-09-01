import random
import uuid
from typing import Dict, Any, List, Tuple
from unittest.mock import PropertyMock

import pytest
from assertpy import assert_that

from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridRefType,
    ShotgridNode,
)
from shotgrid_leecher.repository.utils.hierarchy_traversal import (
    ShotgridNavHierarchyTraversal,
    ShotgridFindHierarchyTraversal,
)

_RAND = random.randint


def _get_random_node(has_children: bool = False) -> Dict[str, Any]:
    types = [x.value for x in list(ShotgridRefType)]
    path = "/".join(
        [str(uuid.uuid4())[-12:] for _ in range(random.randrange(2, 5))]
    )
    parent_path = "/".join(path.split("/")[:-1])
    return {
        "label": f"{random.sample(types, 1)[0]}_{str(uuid.uuid4())[-12:]}",
        "has_children": has_children,
        "children": [],
        "path": path,
        "parent_path": parent_path,
        "ref": {
            "kind": "entity_type",
            "value": random.sample(types, 1)[0],
        },
    }


def _get_bottom_hierarchy(size=10) -> Dict[str, Any]:
    return {
        **_get_random_node(True),
        "children": [_get_random_node() for _ in range(size)],
    }


def _get_middle_hierarchy(size=10) -> Dict[str, Any]:
    return {
        **_get_random_node(True),
        "children": [_get_random_node(True) for _ in range(size)],
    }


def _get_grandchildren(children: List[ShotgridNode]) -> List[ShotgridNode]:
    result: List[ShotgridNode] = []
    for child in children:
        if not child.children:
            result = [*result, child]
        else:
            result = [*result, *_get_grandchildren(child.children)]
    return result


def _lineup_hierarchy(start_from: ShotgridNode) -> List[ShotgridNode]:
    result: List[ShotgridNode] = [start_from]
    for child in start_from.children:
        if not child.children:
            result = [*result, child]
        else:
            result = [*result, *_lineup_hierarchy(child)]
    return result


def _twin_paths(node: ShotgridNode) -> Tuple[List, List]:
    flat = [(x.label, x.parent_paths) for x in _lineup_hierarchy(node)]
    return (
        [x[0] for x in flat[:-1]],
        [x[1].short_path.split("/")[-1] for x in flat[1:]],
    )


def _get_project(id_: int) -> Dict[str, Any]:
    return {
        "Type": "Project",
        "id": id_,
        "code": str(uuid.uuid4()),
    }


def _get_asset_tasks(num: int) -> List[Dict]:
    names = ["lines", "color", "look", "dev"]
    steps = ["modeling", "shading", "rigging"]
    return [
        {
            "id": uuid.uuid4().int,
            "content": random.choice(names),
            "step": {"name": random.choice(steps)},
        }
        for _ in range(num)
    ]


def _get_simple_assets(task_ids: List[int]) -> List[Dict]:
    return [
        {
            "type": "Asset",
            "code": "Fork",
            "sg_asset_type": "PRP",
            "id": random.randint(1, 10_000),
            "tasks": [{"id": x, "type": "Task"} for x in task_ids],
        }
    ]


def test_flat_traversal():
    # Arrange
    client = PropertyMock()
    client.nav_expand = PropertyMock()
    size = 10
    data = _get_bottom_hierarchy(size)
    client.nav_expand.return_value = data
    project_id = random.randint(1, 2000)
    sut = ShotgridNavHierarchyTraversal(project_id, client)
    sut._FIRST_LEVEL_FILTER = [x["label"].lower() for x in data["children"]]
    # Act
    actual = sut.traverse_from_the_top()
    # Assert
    assert_that(actual).is_type_of(ShotgridNode)
    assert_that(actual.children).is_length(10)


@pytest.mark.parametrize(
    "size", list([_RAND(1, 10), _RAND(10, 25), _RAND(25, 55), _RAND(55, 100)])
)
def test_shallow_traversal(size: int):
    # Arrange
    client = PropertyMock()
    client.nav_expand = PropertyMock()
    data = _get_middle_hierarchy(size)
    client.nav_expand.side_effect = [
        data,
        *[_get_bottom_hierarchy(size) for _ in range(size)],
    ]
    project_id = random.randint(1, 2001)
    sut = ShotgridNavHierarchyTraversal(project_id, client)
    sut._FIRST_LEVEL_FILTER = [x["label"].lower() for x in data["children"]]
    # Act
    actual = sut.traverse_from_the_top()
    # Assert
    assert_that(actual).is_type_of(ShotgridNode)
    assert_that(actual.children).is_length(size)
    assert_that(_get_grandchildren(actual.children)).is_length(size * size)


@pytest.mark.parametrize(
    "size", list([_RAND(1, 4), _RAND(4, 9), _RAND(9, 13), _RAND(13, 17)])
)
def test_deep_traversal(size: int):
    # Arrange
    client = PropertyMock()
    client.nav_expand = PropertyMock()
    data = _get_middle_hierarchy(size)
    client.nav_expand.side_effect = [
        data,
        *[_get_middle_hierarchy(size) for _ in range(size)],
        *[_get_bottom_hierarchy(size) for _ in range(size * size * size)],
    ]
    project_id = random.randint(1, 2003)
    sut = ShotgridNavHierarchyTraversal(project_id, client)
    sut._FIRST_LEVEL_FILTER = [x["label"].lower() for x in data["children"]]
    # Act
    actual = sut.traverse_from_the_top()
    # Assert
    assert_that(actual).is_type_of(ShotgridNode)
    assert_that(actual.children).is_length(size)
    assert_that(_get_grandchildren(actual.children)).is_length(
        size * size * size
    )


def test_parent_assignment():
    # Arrange
    size = 1
    client = PropertyMock()
    client.nav_expand = PropertyMock()
    data = _get_middle_hierarchy(size)
    client.nav_expand.side_effect = [
        data,
        *[_get_middle_hierarchy(size) for _ in range(random.randint(10, 25))],
        *[_get_bottom_hierarchy(size) for _ in range(size)],
    ]
    project_id = random.randint(1, 3000)
    sut = ShotgridNavHierarchyTraversal(project_id, client)
    sut._FIRST_LEVEL_FILTER = [x["label"].lower() for x in data["children"]]
    # Act
    actual = sut.traverse_from_the_top()
    # Assert
    assert_that(actual).is_type_of(ShotgridNode)
    assert_that(_twin_paths(actual)[0]).is_equal_to(_twin_paths(actual)[1])


def test_assets_traversal():
    # Arrange
    task_num = 2
    tasks = _get_asset_tasks(task_num)
    asset = _get_simple_assets([x.get("id") for x in tasks])
    project_id = random.randint(10, 1000)
    client = PropertyMock()
    client.find_one.return_value = _get_project(project_id)
    client.find.side_effect = [tasks, asset]

    sut = ShotgridFindHierarchyTraversal(project_id, client)
    # Act
    actual = sut.traverse_from_the_top()
    # Assert
    assert_that(actual).is_type_of(list)
    assert_that(actual).is_length(4 + task_num)
    assert_that([x for x in actual if x["type"] == "Project"]).is_length(1)
    assert_that([x for x in actual if x["type"] == "Group"]).is_length(2)
    assert_that([x for x in actual if x["type"] == "Asset"]).is_length(1)
    assert_that([x for x in actual if x["type"] == "Task"]).is_length(task_num)


def test_assets_traversal_with_unique_task_id():
    # Arrange
    task_num = 100
    tasks = _get_asset_tasks(task_num)
    asset = _get_simple_assets([x.get("id") for x in tasks])
    project_id = random.randint(10, 1000)
    client = PropertyMock()
    client.find_one.return_value = _get_project(project_id)
    client.find.side_effect = [tasks, asset]

    sut = ShotgridFindHierarchyTraversal(project_id, client)
    # Act
    actual = sut.traverse_from_the_top()
    # Assert
    assert_that(
        set([x["_id"] for x in actual if x["type"] == "Task"])
    ).is_length(task_num)
