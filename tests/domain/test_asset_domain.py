import uuid
from datetime import datetime
from unittest.mock import patch, PropertyMock

from assertpy import assert_that

import shotgrid_leecher.domain.asset_domain as domain
from shotgrid_leecher.record.enums import EventTypes
from shotgrid_leecher.record.new_asset_event import NewAssetEvent
from shotgrid_leecher.record.new_event_commands import NewEventCommand
from shotgrid_leecher.record.results import InsertionResult
from shotgrid_leecher.record.shotgrid_subtypes import (
    ShotgridUser,
    ShotgridProject,
    ShotgridEntity,
)


def _get_command() -> NewEventCommand:
    utc_now = datetime.utcnow()
    user = ShotgridUser(2, str(uuid.uuid4()), str(uuid.uuid4()))
    project = ShotgridProject(2, str(uuid.uuid4()), str(uuid.uuid4()))
    entity = ShotgridEntity(2, str(uuid.uuid4()), str(uuid.uuid4()))
    event = NewAssetEvent(2, str(uuid.uuid4()), utc_now, user, project, entity)
    return NewEventCommand(str(uuid.uuid4()), EventTypes.INITIALIZED, event)


@patch(
    "shotgrid_leecher.utils.connectivity.get_collection",
    new_callable=PropertyMock,
)
def test_save_new_asset_events(conn: PropertyMock):
    # Arrange
    expected = InsertionResult(True, [str(uuid.uuid4())])
    collection = PropertyMock()
    command = _get_command()
    conn.return_value = collection
    collection.insert_many.return_value = expected
    # Act
    actual = domain.save_new_asset_events([command])
    # Assert
    assert_that(actual).is_equal_to(expected)
