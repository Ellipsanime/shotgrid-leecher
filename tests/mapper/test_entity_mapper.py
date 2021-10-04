import random
import uuid
from typing import Callable, Dict, TypeVar

import attr
from assertpy import assert_that

from shotgrid_leecher.mapper import entity_mapper
from shotgrid_leecher.record.enums import ShotgridField
from shotgrid_leecher.record.shotgrid_structures import ShotgridAsset, \
    ShotgridShot, ShotgridTask
from shotgrid_leecher.record.shotgrid_subtypes import (
    ProjectFieldsMapping,
    GenericFieldsMapping,
    ShotgridProject,
    AssetFieldsMapping,
    ShotFieldsMapping,
    TaskFieldsMapping,
)

T = TypeVar("T", bound=GenericFieldsMapping, covariant=True)

_PROJ_MAPPING = ProjectFieldsMapping.from_dict({})
_ASSET_MAPPING = AssetFieldsMapping.from_dict({})
_SHOT_MAPPING = ShotFieldsMapping.from_dict({})
_TASK_MAPPING = TaskFieldsMapping.from_dict({})


def _randomize_mapping(
    initial: T,
    ctor: Callable[[Dict], T],
) -> T:
    mapping = {k: str(uuid.uuid4()) for k, v in attr.asdict(initial).items()}
    return ctor(mapping)


def test_to_shotgrid_project():
    # Arrange
    mapping = _randomize_mapping(_PROJ_MAPPING, ProjectFieldsMapping.from_dict)
    data = {k: str(uuid.uuid4()) for k in mapping.mapping_values()}
    # Act
    actual = entity_mapper.to_shotgrid_project(mapping, data)
    # Assert
    assert_that(actual).is_type_of(ShotgridProject)
    assert_that(actual.id).is_not_none()
    assert_that(actual.name).is_not_none()
    assert_that(actual.type).is_not_none()


def test_to_shotgrid_shot():
    # Arrange
    mapping = _randomize_mapping(_SHOT_MAPPING, ShotFieldsMapping.from_dict)
    data = {k: str(uuid.uuid4()) for k in mapping.mapping_values()}
    # Act
    actual: ShotgridShot = entity_mapper.to_shotgrid_shot(mapping, data)
    # Assert
    assert_that(actual).is_type_of(ShotgridShot)
    assert_that(actual.id).is_not_none()
    assert_that(actual.code).is_not_none()
    assert_that(actual.cut_duration).is_not_none()
    assert_that(actual.episode).is_not_none()
    assert_that(actual.sequence).is_not_none()
    assert_that(actual.sequence_episode).is_not_none()
    assert_that(actual.type).is_not_none()


def test_to_shotgrid_task():
    # Arrange
    mapping = _randomize_mapping(_TASK_MAPPING, TaskFieldsMapping.from_dict)
    data = {k: str(uuid.uuid4()) for k in mapping.mapping_values()}
    # Act
    actual: ShotgridTask = entity_mapper.to_shotgrid_task(mapping, data)
    # Assert
    assert_that(actual).is_type_of(ShotgridTask)
    assert_that(actual.id).is_not_none()
    assert_that(actual.entity).is_not_none()
    assert_that(actual.step).is_not_none()
    assert_that(actual.content).is_not_none()


def test_to_shotgrid_asset():
    # Arrange
    tasks_n = random.randint(10, 20)
    asset_mapping = _randomize_mapping(
        _ASSET_MAPPING, AssetFieldsMapping.from_dict
    )
    task_mapping = _randomize_mapping(
        _TASK_MAPPING, TaskFieldsMapping.from_dict
    )
    data = {
        k_1: str(uuid.uuid4())
        if k_1 != ShotgridField.TASKS.value
        else [
            {k_2: str(uuid.uuid4()) for k_2 in task_mapping.mapping_values()}
            for _ in range(tasks_n)
        ]
        for k_1 in asset_mapping.mapping_values()
    }
    # Act
    actual = entity_mapper.to_shotgrid_asset(asset_mapping, task_mapping, data)
    # Assert
    assert_that(actual).is_type_of(ShotgridAsset)
    assert_that(actual.id).is_not_none()
    assert_that(actual.code).is_not_none()
    assert_that(actual.type).is_not_none()
    assert_that(actual.asset_type).is_not_none()
    assert_that(actual.tasks).is_length(tasks_n)
