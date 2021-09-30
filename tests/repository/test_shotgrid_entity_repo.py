import uuid
from dataclasses import asdict
from typing import Any, Callable
from unittest.mock import PropertyMock

from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that

import shotgrid_leecher.repository.shotgrid_entity_repo as sut
import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.mapper.entity_mapper import to_shotgrid_task
from shotgrid_leecher.record.enums import ShotgridTypes
from shotgrid_leecher.record.queries import (
    ShotgridFindProjectByIdQuery,
    ShotgridFindAssetsByProjectQuery,
    ShotgridFindShotsByProjectQuery,
    ShotgridFindTasksByProjectQuery,
)
from shotgrid_leecher.record.shotgrid_structures import ShotgridCredentials
from shotgrid_leecher.record.shotgrid_subtypes import (
    ShotgridProject,
    FieldsMapping,
    ProjectFieldMapping,
    AssetFieldMapping,
    ShotFieldMapping,
    TaskFieldMapping,
)


def _fun(param: Any) -> Callable[[Any], Any]:
    return lambda *_: param


def _credentials():
    return ShotgridCredentials(
        str(uuid.uuid4()),
        str(uuid.uuid4()),
        str(uuid.uuid4()),
    )


def _default_fields_mapping() -> FieldsMapping:
    return FieldsMapping(
        ProjectFieldMapping.from_dict({}),
        AssetFieldMapping.from_dict({}),
        ShotFieldMapping.from_dict({}),
        TaskFieldMapping.from_dict({}),
    )


def test_find_project_by_id(monkeypatch: MonkeyPatch):
    # Arrange
    client = PropertyMock()
    p_id = uuid.uuid4().int
    expected = ShotgridProject(p_id, str(uuid.uuid4()), str(uuid.uuid4()))
    monkeypatch.setattr(conn, "get_shotgrid_client", _fun(client))
    client.find_one.return_value = asdict(expected)
    query = ShotgridFindProjectByIdQuery(
        p_id, _credentials(), _default_fields_mapping().project_mapping
    )
    # Act
    actual = sut.find_project_by_id(query)
    # Assert
    assert_that(actual).is_equal_to(expected)
    client.find_one.assert_called_once_with(
        ShotgridTypes.PROJECT.value,
        [["id", "is", p_id]],
        list(ProjectFieldMapping.from_dict({}).mapping_table.values()),
    )


def test_find_assets_for_project(monkeypatch: MonkeyPatch):
    # Arrange
    client = PropertyMock()
    p_id = uuid.uuid4().int
    project = ShotgridProject(p_id, str(uuid.uuid4()), str(uuid.uuid4()))
    expected = [{str(uuid.uuid4()): uuid.uuid4().int}]
    monkeypatch.setattr(conn, "get_shotgrid_client", _fun(client))
    client.find.return_value = expected
    query = ShotgridFindAssetsByProjectQuery(
        project, _credentials(), _default_fields_mapping().asset_mapping
    )
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
    expected = [{
        "id": uuid.uuid4().int,
        "code": str(uuid.uuid4()),
    }]
    monkeypatch.setattr(conn, "get_shotgrid_client", _fun(client))
    client.find.return_value = expected
    query = ShotgridFindShotsByProjectQuery(
        project, _credentials(), _default_fields_mapping().shot_mapping
    )
    # Act
    actual = sut.find_shots_for_project(query)
    # Assert
    assert_that(actual).is_length(len(expected))
    assert_that(actual[0].id).is_equal_to(expected[0]["id"])
    assert_that(actual[0].code).is_equal_to(expected[0]["code"])
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
    shotgrid_result = [
        {
            "id": uuid.uuid4().int,
            "name": str(uuid.uuid4()),
            "content": str(uuid.uuid4()),
            "entity": {"name": str(uuid.uuid4()), "id": -1},
        }
    ]
    expected = [
        to_shotgrid_task(_default_fields_mapping().task_mapping, x)
        for x in shotgrid_result
    ]
    monkeypatch.setattr(conn, "get_shotgrid_client", _fun(client))
    client.find.return_value = shotgrid_result
    query = ShotgridFindTasksByProjectQuery(
        project,
        _credentials(),
        _default_fields_mapping().task_mapping,
    )
    # Act
    actual = sut.find_tasks_for_project(query)
    # Assert
    assert_that(actual).is_equal_to(expected)
    assert_that(client.find.call_count).is_equal_to(1)
    assert_that(client.find.call_args[0][0]).is_equal_to(
        ShotgridTypes.TASK.value
    )
    assert_that(client.find.call_args[0][1][0][2]).is_equal_to(asdict(project))
