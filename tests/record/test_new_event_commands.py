import datetime
import uuid

from assertpy import assert_that

from shotgrid_leecher.record.enums import EventTypes
from shotgrid_leecher.record.new_asset_event import NewAssetEvent
from shotgrid_leecher.record.new_event_commands import NewEventsCommand
from shotgrid_leecher.record.shotgrid_subtypes import (
    ShotgridProject,
    ShotgridUser,
    ShotgridEntity,
)


def test_new_events_to_list() -> None:
    # Arrange
    now = datetime.datetime.utcnow()
    event_type = EventTypes.INITIALIZED
    user = ShotgridUser(1, str(uuid.uuid4()), str(uuid.uuid4()))
    project = ShotgridProject(1, str(uuid.uuid4()), str(uuid.uuid4()), "")
    entity = ShotgridEntity(1, str(uuid.uuid4()), str(uuid.uuid4()))

    e1 = NewAssetEvent(1, str(uuid.uuid4()), now, user, project, entity)
    e2 = NewAssetEvent(2, str(uuid.uuid4()), now, user, project, entity)

    sut = NewEventsCommand(event_type, [e1, e2])

    # Act
    actual = sut.to_list()

    # Assert
    assert_that(actual).is_type_of(list)
    assert_that(actual).is_length(2)
    assert_that(actual[0].event).is_equal_to(e1)
    assert_that(actual[1].event).is_equal_to(e2)
