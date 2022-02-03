import uuid
from datetime import datetime
from unittest.mock import patch, PropertyMock

from assertpy import assert_that

import domain.asset_domain as domain
from record.enums import EventTypes
from record.new_asset_event import NewAssetEvent
from record.new_event_commands import NewEventCommand
from record.results import InsertionResult
from record.shotgrid_subtypes import (
    ShotgridUser,
    ShotgridProject,
    ShotgridEntity,
)


def _get_command() -> NewEventCommand:
    utc_now = datetime.utcnow()
    user = ShotgridUser(2, str(uuid.uuid4()), str(uuid.uuid4()))
    project = ShotgridProject(2, str(uuid.uuid4()), str(uuid.uuid4()), "")
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
