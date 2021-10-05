import datetime
import random
import uuid

from assertpy import assert_that

from shotgrid_leecher.mapper.asset_events_mapper import (
    new_asset_event_from_dict,
)
from shotgrid_leecher.record.shotgrid_subtypes import (
    ShotgridEntity,
    ShotgridUser,
    ShotgridProject,
)


def _get_meta_dict():
    dic = {
        "type": str(uuid.uuid4()),
        "name": str(uuid.uuid4()),
        "id": random.randint(1, 10_000),
    }
    return dic


def test_new_asset_event_from_dict():
    # Arrange
    entity = _get_meta_dict()
    data = {
        "type": str(uuid.uuid4()),
        "id": random.randint(1, 10_000),
        "event_type": str(uuid.uuid4()),
        "meta": {"entity_id": entity["id"]},
        "entity": entity,
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
    assert_that(actual.shotgrid_name).is_equal_to(data["entity"]["name"])
    assert_that(actual.shotgrid_entity).is_equal_to(ShotgridEntity(**entity))
    assert_that(actual.shotgrid_user).is_equal_to(ShotgridUser(**data["user"]))
    assert_that(actual.shotgrid_project).is_equal_to(
        ShotgridProject(**data["project"])
    )
