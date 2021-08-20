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
    ShotgridHierarchyTraversal,
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


def test_flat_traversal():
    # Arrange
    client = PropertyMock()
    client.nav_expand = PropertyMock()
    size = 10
    data = _get_bottom_hierarchy(size)
    client.nav_expand.return_value = data
    project_id = random.randint(1, 2000)
    sut = ShotgridHierarchyTraversal(project_id, client)
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
    sut = ShotgridHierarchyTraversal(project_id, client)
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
    sut = ShotgridHierarchyTraversal(project_id, client)
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
        *[_get_middle_hierarchy(size) for _ in range(size)],
        *[_get_middle_hierarchy(size) for _ in range(size)],
        *[_get_middle_hierarchy(size) for _ in range(size)],
        *[_get_bottom_hierarchy(size) for _ in range(size)],
    ]
    project_id = random.randint(1, 3000)
    sut = ShotgridHierarchyTraversal(project_id, client)
    sut._FIRST_LEVEL_FILTER = [x["label"].lower() for x in data["children"]]
    # Act
    actual = sut.traverse_from_the_top()
    # Assert
    assert_that(actual).is_type_of(ShotgridNode)
    assert_that(actual.children).is_length(size)
    assert_that(_lineup_hierarchy(actual)).is_length(size * size * size)


def _twin_paths(node: ShotgridNode) -> Tuple[List, List]:
    flat = [(x.label, x.parent_paths) for x in _lineup_hierarchy(node)]

    return [], [flat]
