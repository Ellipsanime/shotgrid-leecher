import random
import uuid
from itertools import chain
from string import ascii_uppercase
from typing import Dict, Any, List, Tuple
from unittest.mock import PropertyMock

import pytest
import shotgrid_leecher.repository.shotgrid_hierarchy_repo as sut
from assertpy import assert_that
from toolz import pipe
from toolz.curried import (
    map as select,
)

_RAND = random.randint


def _get_project(id_: int) -> Dict[str, Any]:
    return {
        "Type": "Project",
        "id": id_,
        "name": f"Project_{str(uuid.uuid4())[-2:]}",
    }


def _get_random_broken_tasks(num: int) -> List[Dict]:
    return [
        {
            "id": uuid.uuid4().int,
            "content": uuid.uuid4(),
            "step": {"name": uuid.uuid4()} if _RAND(1, 10) % 2 == 0 else None,
            "entity": {
                "type": uuid.uuid4(),
                "name": uuid.uuid4(),
                "id": uuid.uuid4().int,
            },
        }
        for _ in range(num)
    ]


def _get_random_assets_with_tasks(
    groups_n: int, num: int
) -> Tuple[List[Dict], List[Dict]]:
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
                    "content": random.choice(names),
                    "step": {"name": random.choice(steps)},
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
        list,
    )
    return assets, tasks


def _get_shut_tasks(shots: List[Dict], num: int) -> List[Dict]:
    names = ["lines", "color", "look", "dev"]
    steps = ["layout", "animation", "render"]
    return list(
        chain(
            *[
                [
                    {
                        "id": uuid.uuid4().int,
                        "content": random.choice(names),
                        "step": {"name": random.choice(steps)},
                        "entity": {
                            "type": "Shot",
                            "name": shot["code"],
                            "id": shot["id"],
                        },
                    }
                    for _ in range(num)
                ]
                for shot in shots
            ]
        )
    )


def _get_full_shots(ep: int, seq: int, num: int, order: int = 1) -> List[Dict]:
    # Shot/EP_OF_SHOT_N/SQ_OF_SHOT_N/SHOT_N/Task_M
    return [
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


def _get_odd_shots(ep: int, seq: int, num: int, order: int = 1) -> List[Dict]:
    # Shot/EP_OF_SHOT_N/SQ_OF_SHOT_N/SHOT_N/Task_M
    return [
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


def _get_shots_without_seq(ep: int, num: int, order: int = 1) -> List[Dict]:
    # Shot/EP_OF_SHOT_N/SHOT_N/Task_M
    return [
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


def _get_shots_without_ep(seq: int, num: int, order: int = 1) -> List[Dict]:
    # Shot/SQ_OF_SHOT_N/SHOT_N/Task_M
    return [
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


@pytest.mark.parametrize(
    "size",
    list([_RAND(10, 25), _RAND(25, 55), _RAND(56, 100)]),
)
def test_random_assets_traversal(size: int):
    # Arrange
    n_group = int(size / 10)
    assets, tasks = _get_random_assets_with_tasks(n_group, size)
    project_id = random.randint(10, 1000)
    client = PropertyMock()
    project = _get_project(project_id)
    client.find_one.return_value = project
    client.find.side_effect = [assets, [], tasks]
    # Arrange
    actual = sut.get_hierarchy_by_project(project_id, client)
    # Act
    assert_that(actual).is_type_of(list)
    assert_that(actual).is_length(n_group * size + n_group * 2 + 2)
    assert_that(actual).path_counts_types(
        f",{project['name']},",
        group=1,
    )
    assert_that(actual).path_counts_types(
        f",{project['name']},Asset,",
        group=n_group,
    )
    assert_that(actual).path_counts_tasks(
        f",{project['name']},Asset,*",
        count=len(tasks),
    )


@pytest.mark.parametrize(
    "size",
    list([_RAND(10, 25), _RAND(25, 55), _RAND(56, 100)]),
)
def test_random_broken_data_traversal(size: int):
    # Arrange
    n_group = int(size / 10)
    assets, asset_tasks = _get_random_assets_with_tasks(n_group, size)
    broken_tasks = _get_random_broken_tasks(size)
    tasks = asset_tasks + broken_tasks
    project_id = random.randint(10, 1000)
    client = PropertyMock()
    project = _get_project(project_id)
    client.find_one.return_value = project
    client.find.side_effect = [assets, [], tasks]
    # Arrange
    actual = sut.get_hierarchy_by_project(project_id, client)
    # Act
    assert_that(actual).is_type_of(list)
    assert_that(actual).is_length(n_group * size + n_group * 2 + 2)
    assert_that(actual).path_counts_tasks(
        f",{project['name']},Asset,*",
        count=len(asset_tasks),
    )


@pytest.mark.parametrize(
    "size",
    list([_RAND(10, 25), _RAND(25, 55), _RAND(56, 100)]),
)
def test_random_complete_traversal(size: int):
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
    client = PropertyMock()
    project = _get_project(project_id)
    client.find_one.return_value = project
    client.find.side_effect = [assets, shots, tasks]
    # Arrange
    actual = sut.get_hierarchy_by_project(project_id, client)
    # Act
    assert_that(actual).path_counts_types(
        f",{project['name']},",
        group=2,
    )
    assert_that(actual).path_counts_types(
        f",{project['name']},Shot,",
        episode=2,
    )
    assert_that(actual).path_counts_types(
        f",{project['name']},Asset,",
        group=n_group,
    )
    assert_that(actual).path_counts_tasks(
        f",{project['name']},Asset,*",
        count=len(asset_tasks),
    )
    assert_that(actual).path_counts_tasks(
        f",{project['name']},Shot,*",
        count=len(shot_tasks),
    )


@pytest.mark.parametrize(
    "size",
    list([_RAND(1, 10), _RAND(10, 25), _RAND(25, 55), _RAND(56, 100)]),
)
def test_random_shots_traversal_at_shot_level(size: int):
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
    client = PropertyMock()
    client.find_one.return_value = project
    client.find.side_effect = [[], shots, tasks]
    # Act
    actual = sut.get_hierarchy_by_project(project_id, client)
    # Assert
    assert_that(actual).path_counts_types(f",{project['name']},", group=1)
    assert_that(actual).path_counts_types(
        f",{project['name']},Shot,",
        episode=2,
        sequence=1,
    )
    assert_that(actual).path_counts_types(
        f",{project['name']},Shot,EP_1,",
        sequence=2,
    )
    assert_that(actual).path_counts_types(
        f",{project['name']},Shot,EP_2,",
        sequence=1,
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project['name']},Shot,EP_1,SQ_1,",
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project['name']},Shot,EP_1,SQ_11,",
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project['name']},Shot,EP_2,SQ_2,",
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project['name']},Shot,SQ_2,",
        shot=size,
    )


@pytest.mark.parametrize(
    "size",
    list([_RAND(1, 10), _RAND(10, 25), _RAND(25, 55), _RAND(56, 100)]),
)
def test_odd_random_shots_traversal_at_shot_level(size: int):
    # Arrange
    shots = [
        *_get_odd_shots(1, 1, size, 1),
        *_get_odd_shots(1, 11, size, 1),
        *_get_odd_shots(2, 2, size, 2),
    ]
    tasks = _get_shut_tasks(shots, size)
    project_id = random.randint(10, 1000)
    project = _get_project(project_id)
    client = PropertyMock()
    client.find_one.return_value = project
    client.find.side_effect = [[], shots, tasks]
    # Act
    actual = sut.get_hierarchy_by_project(project_id, client)
    # Assert
    assert_that(actual).path_counts_types(f",{project['name']},", group=1)
    assert_that(actual).path_counts_types(
        f",{project['name']},Shot,",
        episode=2,
    )
    assert_that(actual).path_counts_types(
        f",{project['name']},Shot,EP_1,",
        sequence=2,
    )
    assert_that(actual).path_counts_types(
        f",{project['name']},Shot,EP_2,",
        sequence=1,
    )
    assert_that(actual).path_counts_types(
        f",{project['name']},Shot,EP_1,SQ_1,",
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project['name']},Shot,EP_1,SQ_11,",
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project['name']},Shot,EP_2,SQ_2,",
        shot=size,
    )


@pytest.mark.parametrize(
    "size",
    list([_RAND(1, 10), _RAND(10, 25), _RAND(25, 55), _RAND(56, 100)]),
)
def test_random_shots_traversal_at_bottom_level(size: int):
    # Arrange
    shots = [
        *_get_full_shots(1, 1, size, 1),
        *_get_full_shots(1, 11, size, 1),
        *_get_full_shots(2, 2, size, 2),
        # *_get_odd_shots(3, 3, size, 3),
        *_get_shots_without_ep(2, size, 4),
        *_get_shots_without_seq(2, size, 5),
    ]
    tasks = _get_shut_tasks(shots, size)
    project_id = random.randint(10, 1000)
    project = _get_project(project_id)
    client = PropertyMock()
    client.find_one.return_value = project
    client.find.side_effect = [[], shots, tasks]
    # Act
    actual = sut.get_hierarchy_by_project(project_id, client)
    # Assert
    assert_that(actual).path_counts_tasks(
        f",{project['name']},Shot,EP_1,SQ_1,SHOT*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project['name']},Shot,EP_1,SQ_11,SHOT*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project['name']},Shot,EP_2,SQ_2,SHOT*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project['name']},Shot,EP_2,SHOT5*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project['name']},Shot,SQ_2,SHOT4*",
        count=size * size,
    )


@pytest.mark.parametrize(
    "size",
    list([_RAND(1, 10), _RAND(10, 25), _RAND(25, 55), _RAND(56, 100)]),
)
def test_odd_random_shots_traversal_at_bottom_level(size: int):
    shots = [
        *_get_odd_shots(1, 1, size, 1),
        *_get_odd_shots(1, 11, size, 1),
        *_get_odd_shots(2, 2, size, 2),
    ]
    # Arrange
    tasks = _get_shut_tasks(shots, size)
    project_id = random.randint(10, 1000)
    project = _get_project(project_id)
    client = PropertyMock()
    client.find_one.return_value = project
    client.find.side_effect = [[], shots, tasks]
    # Act
    actual = sut.get_hierarchy_by_project(project_id, client)
    # Assert
    assert_that(actual).path_counts_tasks(
        f",{project['name']},Shot,EP_1,SQ_1,SHOT*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project['name']},Shot,EP_1,SQ_11,SHOT*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project['name']},Shot,EP_2,SQ_2,SHOT*",
        count=size * size,
    )
