import datetime
import random
import uuid

from assertpy import assert_that

from shotgrid_leecher.mapper.asset_events_mapper import (
    shotgrid_user_from_dict,
    shotgrid_project_from_dict,
    new_asset_event_from_dict,
)


def _get_meta_dict():
    dic = {
        "type": str(uuid.uuid4()),
        "name": str(uuid.uuid4()),
        str(uuid.uuid4()): str(uuid.uuid4()),
        "id": random.randint(1, 10_000),
    }
    return dic


def test_shotgrid_user_from_dict():
    # Arrange
    dic = _get_meta_dict()
    # Act
    actual = shotgrid_user_from_dict(dic)

    # Assert
    assert_that(actual).is_not_none()
    assert_that(actual.type).is_equal_to(dic["type"])
    assert_that(actual.name).is_equal_to(dic["name"])
    assert_that(actual.id).is_equal_to(dic["id"])


def test_shotgrid_project_from_dict():
    # Arrange
    dic = _get_meta_dict()
    # Act
    actual = shotgrid_project_from_dict(dic)

    # Assert
    assert_that(actual).is_not_none()
    assert_that(actual.type).is_equal_to(dic["type"])
    assert_that(actual.name).is_equal_to(dic["name"])
    assert_that(actual.id).is_equal_to(dic["id"])


def test_new_asset_event_from_dict():
    # Arrange
    data = {
        "type": str(uuid.uuid4()),
        "id": random.randint(1, 10_000),
        "event_type": str(uuid.uuid4()),
        "meta": {"entity_id": random.randint(1, 10_000)},
        "entity": None,
        "user": _get_meta_dict(),
        "project": _get_meta_dict(),
        "session_uuid": str(uuid.uuid4()),
        "created_at": datetime.datetime(2020, 9, 21, 14, 2, 45),
    }
    # Act
    actual = new_asset_event_from_dict(data)
    # Assert
    assert_that(actual).is_not_none()
    assert_that(actual.shotgrid_id).is_equal_to(data["id"])
    assert_that(actual.shotgrid_session_uuid).is_equal_to(data["session_uuid"])
    assert_that(actual.shotgrid_entity_id).is_equal_to(
        data["meta"]["entity_id"]
    )
    assert_that(actual.shotgrid_user.type).is_equal_to(data["user"]["type"])
    assert_that(actual.shotgrid_user.name).is_equal_to(data["user"]["name"])
    assert_that(actual.shotgrid_user.id).is_equal_to(data["user"]["id"])
    assert_that(actual.shotgrid_project.type).is_equal_to(
        data["project"]["type"]
    )
    assert_that(actual.shotgrid_project.name).is_equal_to(
        data["project"]["name"]
    )
    assert_that(actual.shotgrid_project.id).is_equal_to(data["project"]["id"])
