import uuid

from assertpy import assert_that

from shotgrid_leecher.record.enums import EventTypes, EventStatuses
from shotgrid_leecher.record.new_asset_event import NewAssetEvent
from shotgrid_leecher.record.new_event_commands import NewEventsCommand
from shotgrid_leecher.record.shotgrid_project import ShotgridProject
from shotgrid_leecher.record.shotgrid_user import ShotgridUser


def test_new_events_to_list() -> None:
    # Arrange
    event_type = EventTypes.CREATION
    event_status = EventStatuses.INIT
    user = ShotgridUser(1, str(uuid.uuid4()), str(uuid.uuid4()))
    project = ShotgridProject(1, str(uuid.uuid4()), str(uuid.uuid4()))

    e1 = NewAssetEvent(1, 1, str(uuid.uuid4()), user, project)
    e2 = NewAssetEvent(2, 2, str(uuid.uuid4()), user, project)

    sut = NewEventsCommand(event_type, event_status, [e1, e2])

    # Act
    actual = sut.to_list()

    # Assert
    assert_that(actual).is_type_of(list)
    assert_that(actual).is_length(2)
    assert_that(actual[0].event).is_equal_to(e1)
    assert_that(actual[1].event).is_equal_to(e2)
