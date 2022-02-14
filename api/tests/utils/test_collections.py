import random
import uuid
from typing import Dict, Any, Tuple

import pytest
from assertpy import assert_that
from mongomock.object_id import ObjectId

from shotgrid_leecher.utils.collections import (
    flatten_dict,
    swap_mapping_keys_values,
)

_RAND = random.randint


def _swap_data(size: int) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    mapping = {str(uuid.uuid4()): str(uuid.uuid4()) for _ in range(size)}
    data = {
        **{v: str(uuid.uuid4()) for k, v in mapping.items()},
        **{str(uuid.uuid4()): str(uuid.uuid4()) for _ in range(size)},
    }
    return mapping, data


def test_flatten_dict_non_dicts():
    # Arrange
    data = {"_id": ObjectId(), uuid.uuid4(): str(uuid.uuid4())}
    # Act
    actual = flatten_dict(data)
    # Assert
    assert_that(actual).is_type_of(dict)
    assert_that(actual).is_length(2)
    assert_that(actual["_id"]).is_equal_to(data["_id"])


def test_flatten_dict_nested_non_dicts():
    # Arrange
    k1, k2, k3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    data = {"_id": ObjectId(), k1: {k2: {k3: k3.int}}}
    # Act
    actual = flatten_dict(data)
    # Assert
    assert_that(actual).is_type_of(dict)
    assert_that(actual.get(f"{k1}.{k2}.{k3}")).is_equal_to(k3.int)


def test_flatten_dict_with_except():
    # Arrange
    def _f():
        return str(uuid.uuid4())[:5]

    k1, k2, k3 = _f(), _f(), _f()
    sub_dict = {1: 1, 2: 2, 3: 3}
    data = {k1: {k2: {k3: sub_dict}}, k3: {k2: {k1: sub_dict}}}
    # Act
    actual = flatten_dict(data, {f"{k1}.{k2}.{k3}"})
    # Assert
    assert_that(set(actual.keys())).is_equal_to(
        {
            f"{k1}.{k2}.{k3}",
            f"{k3}.{k2}.{k1}.1",
            f"{k3}.{k2}.{k1}.2",
            f"{k3}.{k2}.{k1}.3",
        }
    )
    assert_that(actual[f"{k1}.{k2}.{k3}"]).is_equal_to(sub_dict)
    assert_that(actual[f"{k3}.{k2}.{k1}.1"]).is_equal_to(1)
    assert_that(actual[f"{k3}.{k2}.{k1}.2"]).is_equal_to(2)
    assert_that(actual[f"{k3}.{k2}.{k1}.3"]).is_equal_to(3)


def test_flatten_dict_nested_mixed_dicts():
    # Arrange
    k1, k2, k3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    data = {"_id": ObjectId(), k1: {k2: {f"prefix1.54.{k3}": k3.int}}}
    # Act
    actual = flatten_dict(data)
    # Assert
    assert_that(actual).is_type_of(dict)
    assert_that(actual.get(f"{k1}.{k2}.prefix1.54.{k3}")).is_equal_to(k3.int)


def test_flatten_dict_nested_with_lists():
    # Arrange
    k1, k2, k3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    data = {"_ids": [1, 2, 3], k1: {k2: {k3: [1, 2, k3.int]}}}
    # Act
    actual = flatten_dict(data)
    # Assert
    assert_that(actual).is_type_of(dict)
    assert_that(actual.get("_ids")).is_equal_to([1, 2, 3])
    assert_that(actual.get(f"{k1}.{k2}.{k3}")).is_equal_to([1, 2, k3.int])


def test_flatten_dict_nested_with_sets():
    # Arrange
    k1, k2, k3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    data = {"_ids": {1, 2, 3}, k1: {k2: {k3: {1, 2, k3.int}}}}
    # Act
    actual = flatten_dict(data)
    # Assert
    assert_that(actual).is_type_of(dict)
    assert_that(actual.get("_ids")).is_equal_to({1, 2, 3})
    assert_that(actual.get(f"{k1}.{k2}.{k3}")).is_equal_to({1, 2, k3.int})


@pytest.mark.parametrize(
    "data",
    list(
        [
            _swap_data(_RAND(10, 250)),
            _swap_data(_RAND(251, 1555)),
            _swap_data(_RAND(5600, 10_000)),
        ]
    ),
)
def test_swap_mapping_keys_values(data: Tuple[Dict[str, Any], Dict[str, Any]]):
    # Arrange
    mapping, target = data
    # Act
    actual = swap_mapping_keys_values(mapping, target)
    # Assert
    assert_that(actual).is_equal_to(
        {k: target[v] for k, v in mapping.items() if v in target}
    )
