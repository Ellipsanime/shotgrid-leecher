import random
import uuid
from typing import Callable, Dict, TypeVar

import attr
from assertpy import assert_that

from shotgrid_leecher.mapper import entity_mapper
from shotgrid_leecher.record.enums import ShotgridField, ShotgridType
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridAsset,
    ShotgridShot,
    ShotgridTask,
    ShotgridEntityToEntityLink,
)
from shotgrid_leecher.record.shotgrid_subtypes import (
    ProjectFieldsMapping,
    GenericFieldsMapping,
    ShotgridProject,
    AssetFieldsMapping,
    ShotFieldsMapping,
    TaskFieldsMapping,
    ShotToShotLinkMapping,
    AssetToShotLinkMapping,
    AssetToAssetLinkMapping,
)

T = TypeVar("T", bound=GenericFieldsMapping, covariant=True)

_PROJ_MAPPING = ProjectFieldsMapping.from_dict({})
_ASSET_MAPPING = AssetFieldsMapping.from_dict({})
_SHOT_MAPPING = ShotFieldsMapping.from_dict({})
_TASK_MAPPING = TaskFieldsMapping.from_dict({})
_ASSET_TASK_MAPPING = {
    ShotgridField.ID.value: ShotgridField.ID.value,
    ShotgridField.NAME.value: ShotgridField.NAME.value,
    ShotgridField.TYPE.value: ShotgridField.TYPE.value,
}
_SHOT_TO_SHOT_MAPPING = ShotToShotLinkMapping.from_dict({})
_ASSET_TO_SHOT_MAPPING = AssetToShotLinkMapping.from_dict({})
_ASSET_TO_ASSET_MAPPING = AssetToAssetLinkMapping.from_dict({})


_VALUES = {
    ShotgridField.ASSETS.value: [
        {"id": x, "name": str(uuid.uuid4()), "type": str(uuid.uuid4())}
        for x in range(random.randint(5, 10))
    ]
}


def _randomize_mapping(
    initial: T,
    ctor: Callable[[Dict], T],
) -> T:
    mapping = {k: str(uuid.uuid4()) for k, v in attr.asdict(initial).items()}
    return ctor(mapping)


def test_to_shotgrid_project():
    # Arrange
    mapping = _randomize_mapping(_PROJ_MAPPING, ProjectFieldsMapping.from_dict)
    data = {
        k: str(uuid.uuid4()) if k != "id" else 1
        for k in mapping.mapping_values()
    }
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
    data = {
        k: _VALUES.get(k, str(uuid.uuid4())) for k in mapping.mapping_values()
    }
    # Act
    actual: ShotgridShot = entity_mapper.to_shotgrid_shot(mapping, data)
    # Assert
    assert_that(actual).is_type_of(ShotgridShot)
    assert_that(actual.id).is_not_none()
    assert_that(actual.code).is_not_none()
    assert_that(actual.has_params()).is_true()
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
    data = {
        k_1: str(uuid.uuid4())
        if k_1 != ShotgridField.TASKS.value
        else [
            {k_2: str(uuid.uuid4()) for k_2 in _ASSET_TASK_MAPPING}
            for _ in range(tasks_n)
        ]
        for k_1 in asset_mapping.mapping_values()
    }
    # Act
    actual = entity_mapper.to_shotgrid_asset(
        asset_mapping, _TASK_MAPPING, data
    )
    # Assert
    assert_that(actual).is_type_of(ShotgridAsset)
    assert_that(actual.id).is_not_none()
    assert_that(actual.code).is_not_none()
    assert_that(actual.type).is_not_none()
    assert_that(actual.asset_type).is_not_none()
    assert_that(actual.tasks).is_length(tasks_n)


def test_to_shot_to_shot_link():
    # Arrange
    mapping = _randomize_mapping(
        _SHOT_TO_SHOT_MAPPING, ShotToShotLinkMapping.from_dict
    )
    data = {k: str(uuid.uuid4()) for k in mapping.mapping_values()}
    # Act
    actual: ShotgridEntityToEntityLink = entity_mapper.to_shot_to_shot_link(
        mapping,
        data,
    )
    # Assert
    assert_that(actual).is_type_of(ShotgridEntityToEntityLink)
    assert_that(actual.id).is_equal_to(data[ShotgridField.ID.value])
    assert_that(actual.child_id).is_equal_to(
        data[mapping.mapping_table[ShotgridField.LINK_SHOT_ID.value]]
    )
    assert_that(actual.parent_id).is_equal_to(
        data[mapping.mapping_table[ShotgridField.LINK_PARENT_SHOT_ID.value]]
    )
    assert_that(actual.type).is_equal_to(ShotgridType.SHOT_TO_SHOT_LINK.value)
    assert_that(actual.quantity).is_equal_to(data["sg_instance"])


def test_to_shot_to_shot_link_without_quantity():
    # Arrange
    mapping = _randomize_mapping(
        _SHOT_TO_SHOT_MAPPING, ShotToShotLinkMapping.from_dict
    )
    data = {
        k: str(uuid.uuid4())
        for k in mapping.mapping_values()
        if k != "sg_instance"
    }
    # Act
    actual: ShotgridEntityToEntityLink = entity_mapper.to_shot_to_shot_link(
        mapping,
        data,
    )
    # Assert
    assert_that(actual.quantity).is_equal_to(1)


def test_to_asset_to_shot_link():
    # Arrange
    mapping = _randomize_mapping(
        _ASSET_TO_SHOT_MAPPING, AssetToShotLinkMapping.from_dict
    )
    data = {k: str(uuid.uuid4()) for k in mapping.mapping_values()}
    # Act
    actual: ShotgridEntityToEntityLink = entity_mapper.to_asset_to_shot_link(
        mapping,
        data,
    )
    # Assert
    assert_that(actual).is_type_of(ShotgridEntityToEntityLink)
    assert_that(actual.id).is_equal_to(data[ShotgridField.ID.value])
    assert_that(actual.child_id).is_equal_to(
        data[mapping.mapping_table[ShotgridField.LINK_SHOT_ID.value]]
    )
    assert_that(actual.parent_id).is_equal_to(
        data[mapping.mapping_table[ShotgridField.LINK_ASSET_ID.value]]
    )
    assert_that(actual.type).is_equal_to(ShotgridType.ASSET_TO_SHOT_LINK.value)
    assert_that(actual.quantity).is_equal_to(data["sg_instance"])


def test_to_asset_to_shot_link_without_quantity():
    # Arrange
    mapping = _randomize_mapping(
        _ASSET_TO_SHOT_MAPPING, AssetToShotLinkMapping.from_dict
    )
    data = {
        k: str(uuid.uuid4())
        for k in mapping.mapping_values()
        if k != "sg_instance"
    }
    # Act
    actual: ShotgridEntityToEntityLink = entity_mapper.to_asset_to_shot_link(
        mapping,
        data,
    )
    # Assert
    assert_that(actual.quantity).is_equal_to(1)


def test_to_asset_to_asset_link():
    # Arrange
    mapping = _randomize_mapping(
        _ASSET_TO_ASSET_MAPPING, AssetToAssetLinkMapping.from_dict
    )
    data = {k: str(uuid.uuid4()) for k in mapping.mapping_values()}
    # Act
    actual: ShotgridEntityToEntityLink = entity_mapper.to_asset_to_asset_link(
        mapping,
        data,
    )
    # Assert
    assert_that(actual).is_type_of(ShotgridEntityToEntityLink)
    assert_that(actual.id).is_equal_to(data[ShotgridField.ID.value])
    assert_that(actual.child_id).is_equal_to(
        data[mapping.mapping_table[ShotgridField.LINK_ASSET_ID.value]]
    )
    assert_that(actual.parent_id).is_equal_to(
        data[mapping.mapping_table[ShotgridField.LINK_PARENT_ID.value]]
    )
    assert_that(actual.type).is_equal_to(
        ShotgridType.ASSET_TO_ASSET_LINK.value
    )
    assert_that(actual.quantity).is_equal_to(data["sg_instance"])


def test_to_asset_to_asset_link_without_quantity():
    # Arrange
    mapping = _randomize_mapping(
        _ASSET_TO_ASSET_MAPPING, AssetToAssetLinkMapping.from_dict
    )
    data = {
        k: str(uuid.uuid4())
        for k in mapping.mapping_values()
        if k != "sg_instance"
    }
    # Act
    actual: ShotgridEntityToEntityLink = entity_mapper.to_asset_to_asset_link(
        mapping,
        data,
    )
    # Assert
    assert_that(actual.quantity).is_equal_to(1)
