import uuid

from assertpy import assert_that

from record.enums import QueryStringType


def test_query_string_type_from_unknown_type():
    # Arrange
    guid = uuid.uuid4()
    # Act
    actual = QueryStringType.from_param(str(type(guid)))
    # Assert
    assert_that(actual.value).is_equal_to(str)


def test_query_string_type_from_string():
    # Arrange
    # Act
    actual = QueryStringType.from_param("StR")
    # Assert
    assert_that(actual.value).is_equal_to(str)


def test_query_string_type_from_float():
    # Arrange
    # Act
    actual = QueryStringType.from_param("flOaT ")
    # Assert
    assert_that(actual.value).is_equal_to(float)


def test_query_string_type_from_int():
    # Arrange
    # Act
    actual = QueryStringType.from_param(" InT")
    # Assert
    assert_that(actual.value).is_equal_to(int)
