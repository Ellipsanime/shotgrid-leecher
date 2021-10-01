import random
import uuid
from itertools import chain
from string import ascii_uppercase
from typing import Any, List, Tuple, Callable

import pytest
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from toolz import pipe
from toolz.curried import (
    map as select,
)

import shotgrid_leecher.repository.shotgrid_entity_repo as entity_repo
import shotgrid_leecher.repository.shotgrid_hierarchy_repo as sut
from shotgrid_leecher.mapper.entity_mapper import (
    to_shotgrid_task,
    to_shotgrid_shot,
    to_shotgrid_asset,
)
from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.record.queries import ShotgridHierarchyByProjectQuery
from shotgrid_leecher.record.shotgrid_structures import (
    ShotgridCredentials,
    ShotgridTask,
    ShotgridShot, ShotgridAsset,
)
from shotgrid_leecher.record.shotgrid_subtypes import (
    ShotgridProject,
    FieldsMapping,
    ProjectFieldsMapping,
    AssetFieldsMapping,
    ShotFieldsMapping,
    TaskFieldsMapping,
)

_RAND = random.randint


def _fun(param: Any) -> Callable[[Any], Any]:
    return lambda *_: param


def _get_project(id_: int) -> ShotgridProject:
    return ShotgridProject(
        id_,
        f"Project_{str(uuid.uuid4())[-2:]}",
        ShotgridType.PROJECT.value,
    )


def _get_random_broken_tasks(num: int) -> List[ShotgridTask]:
    tasks = [
        {
            "id": uuid.uuid4().int,
            "content": str(uuid.uuid4()),
            "name": str(uuid.uuid4()),
            "step": (
                {"name": str(uuid.uuid4()), "id": -1}
                if _RAND(1, 10) % 2 == 0
                else None
            ),
            "entity": {
                "type": str(uuid.uuid4()),
                "name": str(uuid.uuid4()),
                "id": uuid.uuid4().int,
            },
        }
        for _ in range(num)
    ]
    return pipe(
        tasks,
        select(to_shotgrid_task(_default_fields_mapping().task)),
        list,
    )


def _get_random_assets_with_tasks(
    groups_n: int, num: int
) -> Tuple[List[ShotgridAsset], List[ShotgridTask]]:
    names = ["lines", "color", "look", "dev"]
    steps = ["modeling", "shading", "rigging"]
    assets = [
        {
            "type": "Asset",
            "code": f"Fork{n+1}",
            "sg_asset_type": "".join(
                (random.choice(ascii_uppercase) for _ in range(3))
            ),
            "id": int(f"{n+1}1001"),
            "tasks": [
                {
                    "id": uuid.uuid4().int,
                    "name": str(uuid.uuid4()),
                    "content": random.choice(names),
                    "step": {"name": random.choice(steps), "id": -1},
                    "entity": {
                        "type": "Asset",
                        "name": f"Fork{n+1}",
                        "id": int(f"{n+1}1001"),
                    },
                }
                for _ in range(num)
            ],
        }
        for n in range(groups_n)
    ]

    tasks = pipe(
        assets,
        select(lambda x: x["tasks"]),
        lambda x: chain(*x),
        select(to_shotgrid_task(_default_fields_mapping().task)),
        list,
    )
    return [
        to_shotgrid_asset(
            _default_fields_mapping().asset,
            _default_fields_mapping().task,
            x,
        )
        for x in assets
    ], tasks


def _get_shut_tasks(shots: List[ShotgridShot], num: int) -> List[ShotgridTask]:
    names = ["lines", "color", "look", "dev"]
    steps = ["layout", "animation", "render"]

    tasks = [
        [
            {
                "id": uuid.uuid4().int,
                "content": random.choice(names),
                "name": str(uuid.uuid4()),
                "step": {"name": random.choice(steps), "id": -1},
                "entity": {
                    "type": "Shot",
                    "name": shot.code,
                    "id": shot.id,
                },
            }
            for _ in range(num)
        ]
        for shot in shots
    ]

    return pipe(
        tasks,
        lambda x: chain(*x),
        select(to_shotgrid_task(_default_fields_mapping().task)),
        list,
    )


def _get_full_shots(
    ep: int,
    seq: int,
    num: int,
    order: int = 1,
) -> List[ShotgridShot]:
    # Shot/EP_OF_SHOT_N/SQ_OF_SHOT_N/SHOT_N/Task_M
    shots = [
        {
            "type": "Shot",
            "id": uuid.uuid4().int,
            "sg_sequence": {
                "id": seq,
                "name": f"SQ_{seq}",
                "type": "Sequence",
            },
            "sg_episode": {
                "id": ep,
                "name": f"EP_{ep}",
                "type": "Episode",
            },
            "code": f"SHOT{order}{x}",
            "sg_sequence.Sequence.episode": {
                "id": ep,
                "name": f"EP_{ep}",
                "type": "Episode",
            },
        }
        for x in range(num)
    ]
    return [
        to_shotgrid_shot(_default_fields_mapping().shot, x)
        for x in shots
    ]


def _get_odd_shots(
    ep: int,
    seq: int,
    num: int,
    order: int = 1,
) -> List[ShotgridShot]:
    # Shot/EP_OF_SHOT_N/SQ_OF_SHOT_N/SHOT_N/Task_M
    shots = [
        {
            "type": "Shot",
            "id": uuid.uuid4().int,
            "sg_sequence": {
                "id": seq,
                "name": f"SQ_{seq}",
                "type": "Sequence",
            },
            "code": f"SHOT{order}{x}",
            "sg_sequence.Sequence.episode": {
                "id": ep,
                "name": f"EP_{ep}",
                "type": "Episode",
            },
        }
        for x in range(num)
    ]
    return [
        to_shotgrid_shot(_default_fields_mapping().shot, x)
        for x in shots
    ]


def _get_shots_without_seq(
    ep: int,
    num: int,
    order: int = 1,
) -> List[ShotgridShot]:
    # Shot/EP_OF_SHOT_N/SHOT_N/Task_M
    shots = [
        {
            "type": "Shot",
            "id": uuid.uuid4().int,
            "sg_episode": {
                "id": ep,
                "name": f"EP_{ep}",
                "type": "Episode",
            },
            "code": f"SHOT{order}{x}",
        }
        for x in range(num)
    ]
    return [
        to_shotgrid_shot(_default_fields_mapping().shot, x)
        for x in shots
    ]


def _get_shots_without_ep(
    seq: int,
    num: int,
    order: int = 1,
) -> List[ShotgridShot]:
    # Shot/SQ_OF_SHOT_N/SHOT_N/Task_M
    shots = [
        {
            "type": "Shot",
            "id": 100 + order + x,
            "sg_sequence": {
                "id": seq,
                "name": f"SQ_{seq}",
                "type": "Sequence",
            },
            "code": f"SHOT{order}{x}",
        }
        for x in range(num)
    ]
    return [
        to_shotgrid_shot(_default_fields_mapping().shot, x)
        for x in shots
    ]


def _default_fields_mapping() -> FieldsMapping:
    return FieldsMapping(
        ProjectFieldsMapping.from_dict({}),
        AssetFieldsMapping.from_dict({}),
        ShotFieldsMapping.from_dict({}),
        TaskFieldsMapping.from_dict({}),
    )


def _patch_repo(
    monkeypatch: MonkeyPatch,
    project: ShotgridProject,
    assets: List,
    shots: List,
    tasks: List,
) -> None:
    monkeypatch.setattr(entity_repo, "find_project_by_id", _fun(project))
    monkeypatch.setattr(entity_repo, "find_assets_for_project", _fun(assets))
    monkeypatch.setattr(entity_repo, "find_shots_for_project", _fun(shots))
    monkeypatch.setattr(entity_repo, "find_tasks_for_project", _fun(tasks))


def _to_query(project_id: int) -> ShotgridHierarchyByProjectQuery:
    return ShotgridHierarchyByProjectQuery(
        project_id,
        ShotgridCredentials("", "", ""),
        _default_fields_mapping(),
    )


@pytest.mark.parametrize(
    "size",
    list([_RAND(10, 25), _RAND(25, 55), _RAND(56, 100)]),
)
def test_random_assets_traversal(monkeypatch: MonkeyPatch, size: int):
    # Arrange
    n_group = int(size / 10)
    assets, tasks = _get_random_assets_with_tasks(n_group, size)
    project_id = random.randint(10, 1000)
    project = _get_project(project_id)
    _patch_repo(monkeypatch, project, assets, [], tasks)
    # Arrange
    actual = sut.get_hierarchy_by_project(_to_query(project_id))
    # Act
    assert_that(actual).is_type_of(list)
    assert_that(actual).is_length(n_group * size + n_group * 2 + 2)
    assert_that(actual).path_counts_types(
        f",{project.name},",
        group=1,
    )
    assert_that(actual).path_counts_types(
        f",{project.name},Asset,",
        group=n_group,
    )
    assert_that(actual).path_counts_tasks(
        f",{project.name},Asset,*",
        count=len(tasks),
    )


@pytest.mark.parametrize(
    "size",
    list([_RAND(10, 25), _RAND(25, 55), _RAND(56, 100)]),
)
def test_random_broken_data_traversal(monkeypatch: MonkeyPatch, size: int):
    # Arrange
    n_group = int(size / 10)
    assets, asset_tasks = _get_random_assets_with_tasks(n_group, size)
    broken_tasks = _get_random_broken_tasks(size)
    tasks = asset_tasks + broken_tasks
    project_id = random.randint(10, 1000)
    project = _get_project(project_id)
    _patch_repo(monkeypatch, project, assets, [], tasks)
    # Arrange
    actual = sut.get_hierarchy_by_project(_to_query(project_id))
    # Act
    assert_that(actual).is_type_of(list)
    assert_that(actual).is_length(n_group * size + n_group * 2 + 2)
    assert_that(actual).path_counts_tasks(
        f",{project.name},Asset,*",
        count=len(asset_tasks),
    )


@pytest.mark.parametrize(
    "size",
    list([_RAND(10, 25), _RAND(25, 55), _RAND(56, 100)]),
)
def test_random_complete_traversal(monkeypatch: MonkeyPatch, size: int):
    # Arrange
    n_group = int(size / 10)
    shots = [
        *_get_full_shots(1, 1, size, 1),
        *_get_full_shots(1, 11, size, 1),
        *_get_full_shots(2, 2, size, 2),
    ]
    shot_tasks = _get_shut_tasks(shots, size)
    assets, asset_tasks = _get_random_assets_with_tasks(n_group, size)
    tasks = shot_tasks + asset_tasks
    project_id = random.randint(10, 1000)
    project = _get_project(project_id)
    _patch_repo(monkeypatch, project, assets, shots, tasks)
    # Arrange
    actual = sut.get_hierarchy_by_project(_to_query(project_id))
    # Act
    assert_that(actual).path_counts_types(
        f",{project.name},",
        group=2,
    )
    assert_that(actual).path_counts_types(
        f",{project.name},Shot,",
        episode=2,
    )
    assert_that(actual).path_counts_types(
        f",{project.name},Asset,",
        group=n_group,
    )
    assert_that(actual).path_counts_tasks(
        f",{project.name},Asset,*",
        count=len(asset_tasks),
    )
    assert_that(actual).path_counts_tasks(
        f",{project.name},Shot,*",
        count=len(shot_tasks),
    )


@pytest.mark.parametrize(
    "size",
    list([_RAND(1, 10), _RAND(10, 25), _RAND(25, 55), _RAND(56, 100)]),
)
def test_random_shots_traversal_at_shot_level(
    monkeypatch: MonkeyPatch, size: int
):
    # Arrange
    shots = [
        *_get_full_shots(1, 1, size, 1),
        *_get_full_shots(1, 11, size, 1),
        *_get_full_shots(2, 2, size, 2),
        *_get_shots_without_ep(2, size, 4),
        *_get_shots_without_seq(2, size, 5),
    ]
    tasks = _get_shut_tasks(shots, size)
    project_id = random.randint(10, 1000)
    project = _get_project(project_id)
    _patch_repo(monkeypatch, project, [], shots, tasks)
    # Act
    actual = sut.get_hierarchy_by_project(_to_query(project_id))
    # Assert
    assert_that(actual).path_counts_types(f",{project.name},", group=1)
    assert_that(actual).path_counts_types(
        f",{project.name},Shot,",
        episode=2,
        sequence=1,
    )
    assert_that(actual).path_counts_types(
        f",{project.name},Shot,EP_1,",
        sequence=2,
    )
    assert_that(actual).path_counts_types(
        f",{project.name},Shot,EP_2,",
        sequence=1,
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project.name},Shot,EP_1,SQ_1,",
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project.name},Shot,EP_1,SQ_11,",
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project.name},Shot,EP_2,SQ_2,",
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project.name},Shot,SQ_2,",
        shot=size,
    )


@pytest.mark.parametrize(
    "size",
    list([_RAND(1, 10), _RAND(10, 25), _RAND(25, 55), _RAND(56, 100)]),
)
def test_odd_random_shots_traversal_at_shot_level(
    monkeypatch: MonkeyPatch, size: int
):
    # Arrange
    shots = [
        *_get_odd_shots(1, 1, size, 1),
        *_get_odd_shots(1, 11, size, 1),
        *_get_odd_shots(2, 2, size, 2),
    ]
    tasks = _get_shut_tasks(shots, size)
    project_id = random.randint(10, 1000)
    project = _get_project(project_id)
    _patch_repo(monkeypatch, project, [], shots, tasks)
    # Act
    actual = sut.get_hierarchy_by_project(_to_query(project_id))
    # Assert
    assert_that(actual).path_counts_types(f",{project.name},", group=1)
    assert_that(actual).path_counts_types(
        f",{project.name},Shot,",
        episode=2,
    )
    assert_that(actual).path_counts_types(
        f",{project.name},Shot,EP_1,",
        sequence=2,
    )
    assert_that(actual).path_counts_types(
        f",{project.name},Shot,EP_2,",
        sequence=1,
    )
    assert_that(actual).path_counts_types(
        f",{project.name},Shot,EP_1,SQ_1,",
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project.name},Shot,EP_1,SQ_11,",
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project.name},Shot,EP_2,SQ_2,",
        shot=size,
    )


@pytest.mark.parametrize(
    "size",
    list([_RAND(1, 10), _RAND(10, 25), _RAND(25, 55), _RAND(56, 100)]),
)
def test_random_shots_traversal_at_bottom_level(
    monkeypatch: MonkeyPatch, size: int
):
    # Arrange
    shots = [
        *_get_full_shots(1, 1, size, 1),
        *_get_full_shots(1, 11, size, 1),
        *_get_full_shots(2, 2, size, 2),
        *_get_shots_without_ep(2, size, 4),
        *_get_shots_without_seq(2, size, 5),
    ]
    tasks = _get_shut_tasks(shots, size)
    project_id = random.randint(10, 1000)
    project = _get_project(project_id)
    _patch_repo(monkeypatch, project, [], shots, tasks)
    # Act
    actual = sut.get_hierarchy_by_project(_to_query(project_id))
    # Assert
    assert_that(actual).path_counts_tasks(
        f",{project.name},Shot,EP_1,SQ_1,SHOT*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project.name},Shot,EP_1,SQ_11,SHOT*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project.name},Shot,EP_2,SQ_2,SHOT*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project.name},Shot,EP_2,SHOT5*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project.name},Shot,SQ_2,SHOT4*",
        count=size * size,
    )


@pytest.mark.parametrize(
    "size",
    list([_RAND(1, 10), _RAND(10, 25), _RAND(25, 55), _RAND(56, 100)]),
)
def test_odd_random_shots_traversal_at_bottom_level(
    monkeypatch: MonkeyPatch, size: int
):
    # Arrange
    shots = [
        *_get_odd_shots(1, 11, size, 1),
        *_get_odd_shots(1, 1, size, 1),
        *_get_odd_shots(2, 2, size, 2),
    ]
    project_id = random.randint(10, 1000)
    tasks = _get_shut_tasks(shots, size)
    project = _get_project(project_id)
    _patch_repo(monkeypatch, project, [], shots, tasks)
    # Act
    actual = sut.get_hierarchy_by_project(_to_query(project_id))
    # Assert
    assert_that(actual).path_counts_tasks(
        f",{project.name},Shot,EP_1,SQ_1,SHOT*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project.name},Shot,EP_1,SQ_11,SHOT*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project.name},Shot,EP_2,SQ_2,SHOT*",
        count=size * size,
    )
