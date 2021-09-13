import uuid
from dataclasses import asdict
from typing import Any, Callable
from unittest.mock import PropertyMock

from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that

import shotgrid_leecher.repository.shotgrid_entity_repo as sut
import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.record.enums import ShotgridTypes
from shotgrid_leecher.record.queries import (
    ShotgridFindProjectByIdQuery,
    ShotgridFindAssetsByProjectQuery, ShotgridFindShotsByProjectQuery,
    ShotgridFindTasksByProjectQuery,
)
from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials
from shotgrid_leecher.record.shotgrid_subtypes import ShotgridProject


def _fun(param: Any) -> Callable[[Any], Any]:
    return lambda *_: param


def _credentials():
    return ShotgridCredentials(
        str(uuid.uuid4()),
        str(uuid.uuid4()),
        str(uuid.uuid4()),
    )


def test_find_project_by_id(monkeypatch: MonkeyPatch):
    # Arrange
    client = PropertyMock()
    p_id = uuid.uuid4().int
    expected = ShotgridProject(p_id, str(uuid.uuid4()), str(uuid.uuid4()))
    monkeypatch.setattr(conn, "get_shotgrid_client", _fun(client))
    client.find_one.return_value = asdict(expected)
    query = ShotgridFindProjectByIdQuery(p_id, _credentials())
    # Act
    actual = sut.find_project_by_id(query)
    # Assert
    assert_that(actual).is_equal_to(expected)
    client.find_one.assert_called_once_with(
        ShotgridTypes.PROJECT.value, [["id", "is", p_id]], ["name"]
    )


def test_find_assets_for_project(monkeypatch: MonkeyPatch):
    # Arrange
    client = PropertyMock()
    p_id = uuid.uuid4().int
    project = ShotgridProject(p_id, str(uuid.uuid4()), str(uuid.uuid4()))
    expected = [{str(uuid.uuid4()): uuid.uuid4().int}]
    monkeypatch.setattr(conn, "get_shotgrid_client", _fun(client))
    client.find.return_value = expected
    query = ShotgridFindAssetsByProjectQuery(project, _credentials())
    # Act
    actual = sut.find_assets_for_project(query)
    # Assert
    assert_that(actual).is_equal_to(expected)
    assert_that(client.find.call_count).is_equal_to(1)
    assert_that(client.find.call_args[0][0]).is_equal_to(
        ShotgridTypes.ASSET.value
    )
    assert_that(client.find.call_args[0][1][0][2]).is_equal_to(asdict(project))


def test_find_shots_for_project(monkeypatch: MonkeyPatch):
    # Arrange
    client = PropertyMock()
    p_id = uuid.uuid4().int
    project = ShotgridProject(p_id, str(uuid.uuid4()), str(uuid.uuid4()))
    expected = [{str(uuid.uuid4()): uuid.uuid4().int}]
    monkeypatch.setattr(conn, "get_shotgrid_client", _fun(client))
    client.find.return_value = expected
    query = ShotgridFindShotsByProjectQuery(project, _credentials())
    # Act
    actual = sut.find_shots_for_project(query)
    # Assert
    assert_that(actual).is_equal_to(expected)
    assert_that(client.find.call_count).is_equal_to(1)
    assert_that(client.find.call_args[0][0]).is_equal_to(
        ShotgridTypes.SHOT.value
    )
    assert_that(client.find.call_args[0][1][0][2]).is_equal_to(asdict(project))


def test_find_tasks_for_project(monkeypatch: MonkeyPatch):
    # Arrange
    client = PropertyMock()
    p_id = uuid.uuid4().int
    project = ShotgridProject(p_id, str(uuid.uuid4()), str(uuid.uuid4()))
    expected = [{str(uuid.uuid4()): uuid.uuid4().int}]
    monkeypatch.setattr(conn, "get_shotgrid_client", _fun(client))
    client.find.return_value = expected
    query = ShotgridFindTasksByProjectQuery(project, _credentials())
    # Act
    actual = sut.find_tasks_for_project(query)
    # Assert
    assert_that(actual).is_equal_to(expected)
    assert_that(client.find.call_count).is_equal_to(1)
    assert_that(client.find.call_args[0][0]).is_equal_to(
        ShotgridTypes.TASK.value
    )
    assert_that(client.find.call_args[0][1][0][2]).is_equal_to(asdict(project))
