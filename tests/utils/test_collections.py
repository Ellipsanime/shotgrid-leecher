import uuid

from assertpy import assert_that
from mongomock.object_id import ObjectId

from shotgrid_leecher.utils.collections import flatten_dict


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
