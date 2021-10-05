import uuid
from dataclasses import asdict
from typing import Any, Callable
from unittest.mock import PropertyMock

from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that

import shotgrid_leecher.repository.shotgrid_entity_repo as sut
import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.mapper import entity_mapper
from shotgrid_leecher.mapper.entity_mapper import to_shotgrid_task
from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.record.queries import (
    ShotgridFindProjectByIdQuery,
    ShotgridFindAssetsByProjectQuery,
    ShotgridFindShotsByProjectQuery,
    ShotgridFindTasksByProjectQuery,
)
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridCredentials,
    ShotgridAsset,
)
from shotgrid_leecher.record.shotgrid_subtypes import (
    ShotgridProject,
    FieldsMapping,
    ProjectFieldsMapping,
    AssetFieldsMapping,
    ShotFieldsMapping,
    TaskFieldsMapping,
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
        ProjectFieldsMapping.from_dict({}),
        AssetFieldsMapping.from_dict({}),
        ShotFieldsMapping.from_dict({}),
        TaskFieldsMapping.from_dict({}),
    )


def test_find_project_by_id(monkeypatch: MonkeyPatch):
    # Arrange
    client = PropertyMock()
    p_id = uuid.uuid4().int
    expected = ShotgridProject(p_id, str(uuid.uuid4()), str(uuid.uuid4()))
    monkeypatch.setattr(conn, "get_shotgrid_client", _fun(client))
    client.find_one.return_value = asdict(expected)
    query = ShotgridFindProjectByIdQuery(
        p_id, _credentials(), _default_fields_mapping().project
    )
    # Act
    actual = sut.find_project_by_id(query)
    # Assert
    assert_that(actual).is_equal_to(expected)
    client.find_one.assert_called_once_with(
        ShotgridType.PROJECT.value,
        [["id", "is", p_id]],
        list(ProjectFieldsMapping.from_dict({}).mapping_table.values()),
    )


def test_find_assets_for_project(monkeypatch: MonkeyPatch):
    # Arrange
    client = PropertyMock()
    mapper = PropertyMock()
    p_id = uuid.uuid4().int
    project = ShotgridProject(p_id, str(uuid.uuid4()), str(uuid.uuid4()))
    asset = ShotgridAsset(1, "", "", "", [])
    raw_assets = [{str(uuid.uuid4()): uuid.uuid4().int}]
    monkeypatch.setattr(conn, "get_shotgrid_client", _fun(client))
    monkeypatch.setattr(entity_mapper, "to_shotgrid_asset", mapper)
    client.find.return_value = raw_assets
    mapper.return_value = asset
    asset_mapping = _default_fields_mapping().asset
    task_mapping = _default_fields_mapping().task
    query = ShotgridFindAssetsByProjectQuery(
        project,
        _credentials(),
        asset_mapping,
        task_mapping,
    )
    # Act
    actual = sut.find_assets_for_project(query)
    # Assert
    assert_that(actual).is_equal_to([asset])
    assert_that(mapper.call_args[0]).is_equal_to(
        (asset_mapping, task_mapping, raw_assets[0])
    )
    assert_that(client.find.call_count).is_equal_to(1)
    assert_that(client.find.call_args[0][0]).is_equal_to(
        ShotgridType.ASSET.value
    )
    assert_that(client.find.call_args[0][1][0][2]).is_equal_to(asdict(project))


def test_find_shots_for_project(monkeypatch: MonkeyPatch):
    # Arrange
    client = PropertyMock()
    p_id = uuid.uuid4().int
    project = ShotgridProject(p_id, str(uuid.uuid4()), str(uuid.uuid4()))
    expected = [
        {
            "id": uuid.uuid4().int,
            "code": str(uuid.uuid4()),
        }
    ]
    monkeypatch.setattr(conn, "get_shotgrid_client", _fun(client))
    client.find.return_value = expected
    query = ShotgridFindShotsByProjectQuery(
        project, _credentials(), _default_fields_mapping().shot
    )
    # Act
    actual = sut.find_shots_for_project(query)
    # Assert
    assert_that(actual).is_length(len(expected))
    assert_that(actual[0].id).is_equal_to(expected[0]["id"])
    assert_that(actual[0].code).is_equal_to(expected[0]["code"])
    assert_that(client.find.call_count).is_equal_to(1)
    assert_that(client.find.call_args[0][0]).is_equal_to(
        ShotgridType.SHOT.value
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
        to_shotgrid_task(_default_fields_mapping().task, x)
        for x in shotgrid_result
    ]
    monkeypatch.setattr(conn, "get_shotgrid_client", _fun(client))
    client.find.return_value = shotgrid_result
    query = ShotgridFindTasksByProjectQuery(
        project,
        _credentials(),
        _default_fields_mapping().task,
    )
    # Act
    actual = sut.find_tasks_for_project(query)
    # Assert
    assert_that(actual).is_equal_to(expected)
    assert_that(client.find.call_count).is_equal_to(1)
    assert_that(client.find.call_args[0][0]).is_equal_to(
        ShotgridType.TASK.value
    )
    assert_that(client.find.call_args[0][1][0][2]).is_equal_to(asdict(project))
