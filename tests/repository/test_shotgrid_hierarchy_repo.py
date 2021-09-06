import random
import uuid
from itertools import chain
from typing import Dict, Any, List
from unittest.mock import PropertyMock

import pytest
from assertpy import assert_that

import shotgrid_leecher.repository.shotgrid_hierarchy_repo as sut

_RAND = random.randint


def _get_project(id_: int) -> Dict[str, Any]:
    return {
        "Type": "Project",
        "id": id_,
        "code": f"Project_{str(uuid.uuid4())[-2:]}",
    }


def _get_asset_tasks(num: int) -> List[Dict]:
    names = ["lines", "color", "look", "dev"]
    steps = ["modeling", "shading", "rigging"]
    return [
        {
            "id": uuid.uuid4().int,
            "content": random.choice(names),
            "step": {"name": random.choice(steps)},
            "entity": {"type": "Asset", "name": "Fork", "id": 10000},
        }
        for _ in range(num)
    ]


def _get_simple_assets(task_ids: List[int]) -> List[Dict]:
    return [
        {
            "type": "Asset",
            "code": "Fork",
            "sg_asset_type": "PRP",
            "id": 10000,
            "tasks": [{"id": x, "type": "Task"} for x in task_ids],
        }
    ]


def _get_random_assets(task_ids: List[int]) -> List[Dict]:
    groups_n = int(len(task_ids) / 10) + 1

    return [
        {
            "type": "Asset",
            "code": "Fork",
            "sg_asset_type": "PRP",
            "id": 10000,
            "tasks": [{"id": x, "type": "Task"} for x in task_ids],
        }
        for x in range(num)
    ]


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


def _get_shot_tasks() -> List[Dict]:
    names = ["lines", "color", "look", "dev"]
    steps = ["layout", "animation", "render"]
    return [
        {
            "id": uuid.uuid4().int,
            "content": random.choice(names),
            "step": {"name": random.choice(steps)},
            "entity": {"type": "Shot", "name": "Empty1", "id": 100000},
        },
        {
            "id": uuid.uuid4().int,
            "content": random.choice(names),
            "step": {"name": random.choice(steps)},
            "entity": {"type": "Shot", "name": "SHOT2", "id": 100001},
        },
        {
            "id": uuid.uuid4().int,
            "content": random.choice(names),
            "step": {"name": random.choice(steps)},
            "entity": {"type": "Shot", "name": "SHOT3", "id": 100002},
        },
        {
            "id": uuid.uuid4().int,
            "content": random.choice(names),
            "step": {"name": random.choice(steps)},
            "entity": {"type": "Shot", "name": "SHOT4", "id": 100003},
        },
    ]


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


def _get_shots() -> List[Dict]:
    return [
        {
            "type": "Shot",
            "id": 100000,
            "sg_sequence": None,
            "sg_episode": None,
            "sg_sequence.Sequence.episode": None,
            "code": "Empty1",
        },
        {
            "type": "Shot",
            "id": 100001,
            "sg_sequence": None,
            "sg_episode": {
                "id": 230,
                "name": "EP_OF_SHOT2",
                "type": "Episode",
            },
            "sg_cut_duration": None,
            "sg_frame_rate": None,
            "code": "SHOT2",
            "sg_sequence.Sequence.episode": None,
        },
        {
            "type": "Shot",
            "id": 100002,
            "sg_sequence": {
                "id": 132,
                "name": "SQ_OF_SHOT3",
                "type": "Sequence",
            },
            "sg_episode": None,
            "sg_cut_duration": None,
            "sg_frame_rate": None,
            "code": "SHOT3",
            "sg_sequence.Sequence.episode": None,
        },
        {
            "type": "Shot",
            "id": 100003,
            "sg_sequence": {
                "id": 132,
                "name": "SQ_OF_SHOT4",
                "type": "Sequence",
            },
            "sg_episode": {
                "id": 232,
                "name": "EP_OF_SHOT4",
                "type": "Episode",
            },
            "sg_cut_duration": None,
            "sg_frame_rate": None,
            "code": "SHOT4",
            "sg_sequence.Sequence.episode": {
                "id": 232,
                "name": "EP_OF_SHOT4",
                "type": "Episode",
            },
        },
    ]


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
    assert_that(actual).path_counts_types(f",{project['code']},", group=1)
    assert_that(actual).path_counts_types(
        f",{project['code']},Shot,",
        episode=2,
        sequence=1,
    )
    assert_that(actual).path_counts_types(
        f",{project['code']},Shot,EP_1,",
        sequence=2,
    )
    assert_that(actual).path_counts_types(
        f",{project['code']},Shot,EP_2,",
        sequence=1,
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project['code']},Shot,EP_1,SQ_1,",
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project['code']},Shot,EP_1,SQ_11,",
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project['code']},Shot,EP_2,SQ_2,",
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project['code']},Shot,SQ_2,",
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
    assert_that(actual).path_counts_types(f",{project['code']},", group=1)
    assert_that(actual).path_counts_types(
        f",{project['code']},Shot,",
        episode=2,
    )
    assert_that(actual).path_counts_types(
        f",{project['code']},Shot,EP_1,",
        sequence=2,
    )
    assert_that(actual).path_counts_types(
        f",{project['code']},Shot,EP_2,",
        sequence=1,
    )
    assert_that(actual).path_counts_types(
        f",{project['code']},Shot,EP_1,SQ_1,",
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project['code']},Shot,EP_1,SQ_11,",
        shot=size,
    )
    assert_that(actual).path_counts_types(
        f",{project['code']},Shot,EP_2,SQ_2,",
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
        f",{project['code']},Shot,EP_1,SQ_1,SHOT*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project['code']},Shot,EP_1,SQ_11,SHOT*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project['code']},Shot,EP_2,SQ_2,SHOT*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project['code']},Shot,EP_2,SHOT5*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project['code']},Shot,SQ_2,SHOT4*",
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
        f",{project['code']},Shot,EP_1,SQ_1,SHOT*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project['code']},Shot,EP_1,SQ_11,SHOT*",
        count=size * size,
    )
    assert_that(actual).path_counts_tasks(
        f",{project['code']},Shot,EP_2,SQ_2,SHOT*",
        count=size * size,
    )


def test_shots_traversal():
    # Arrange
    tasks = _get_shot_tasks()
    shots = _get_shots()
    project_id = random.randint(10, 1000)
    client = PropertyMock()
    client.find_one.return_value = _get_project(project_id)
    client.find.side_effect = [[], shots, tasks]
    # Act
    actual = sut.get_hierarchy_by_project(project_id, client)
    # Assert
    assert_that(actual).is_length(14)


def test_shots_traversal_hierarchy():
    # Arrange
    tasks = _get_shot_tasks()
    shots = _get_shots()
    project_id = random.randint(10, 1000)
    client = PropertyMock()
    project = _get_project(project_id)
    client.find_one.return_value = project
    client.find.side_effect = [[], shots, tasks]

    # Act
    actual = sut.get_hierarchy_by_project(project_id, client)
    # Assert
    assert_that(actual).path_has_types(None, ["Project"])
    assert_that(actual).path_has_types(f",{project['code']},", ["Group"])
    assert_that(actual).path_has_types(
        f",{project['code']},Shot,",
        ["Shot", "Episode", "Episode", "Sequence"],
    )
    assert_that(actual).path_has_types(
        f",{project['code']},Shot,EP_OF_SHOT2,",
        ["Shot"],
    )
    assert_that(actual).path_has_types(
        f",{project['code']},Shot,SQ_OF_SHOT3,",
        ["Shot"],
    )
    assert_that(actual).path_has_types(
        f",{project['code']},Shot,Empty1,",
        ["Task"],
    )
    assert_that(actual).path_has_types(
        f",{project['code']},Shot,EP_OF_SHOT4,",
        ["Sequence"],
    )
    assert_that(actual).path_has_types(
        f",{project['code']},Shot,EP_OF_SHOT4,SQ_OF_SHOT4,",
        ["Shot"],
    )
    assert_that(actual).path_has_types(
        f",{project['code']},Shot,EP_OF_SHOT2,SHOT2,",
        ["Task"],
    )
    assert_that(actual).path_has_types(
        f",{project['code']},Shot,SQ_OF_SHOT3,SHOT3,",
        ["Task"],
    )
    assert_that(actual).path_has_types(
        f",{project['code']},Shot,EP_OF_SHOT4,SQ_OF_SHOT4,SHOT4,",
        ["Task"],
    )


def test_assets_traversal_hierarchy():
    # Arrange
    task_num = 2
    tasks = _get_asset_tasks(task_num)
    asset = _get_simple_assets([x.get("id") for x in tasks])
    project_id = random.randint(10, 1000)
    client = PropertyMock()
    project = _get_project(project_id)
    client.find_one.return_value = project
    client.find.side_effect = [asset, [], tasks]

    # Act
    actual = sut.get_hierarchy_by_project(project_id, client)

    # Assert
    assert_that(actual).path_has_types(None, ["Project"])
    assert_that(actual).path_has_types(f",{project['code']},", ["Group"])
    assert_that(actual).path_has_types(
        f",{project['code']},Asset,",
        ["Group"],
    )
    assert_that(actual).path_has_types(
        f",{project['code']},Asset,PRP,",
        ["Asset"],
    )
    assert_that(actual).path_has_types(
        f",{project['code']},Asset,PRP,{asset[0]['code']},",
        ["Task", "Task"],
    )


def test_assets_traversal():
    # Arrange
    task_num = 2
    tasks = _get_asset_tasks(task_num)
    asset = _get_simple_assets([x.get("id") for x in tasks])
    project_id = random.randint(10, 1000)
    client = PropertyMock()
    client.find_one.return_value = _get_project(project_id)
    client.find.side_effect = [asset, [], tasks]

    # Act
    actual = sut.get_hierarchy_by_project(project_id, client)
    # Assert
    assert_that(actual).is_type_of(list)
    assert_that(actual).is_length(4 + task_num)
    assert_that([x for x in actual if x["type"] == "Project"]).is_length(1)
    assert_that([x for x in actual if x["type"] == "Group"]).is_length(2)
    assert_that([x for x in actual if x["type"] == "Asset"]).is_length(1)
    assert_that([x for x in actual if x["type"] == "Task"]).is_length(task_num)


def test_assets_traversal_with_unique_task_id():
    # Arrange
    task_num = 100
    tasks = _get_asset_tasks(task_num)
    asset = _get_simple_assets([x.get("id") for x in tasks])
    project_id = random.randint(10, 1000)
    client = PropertyMock()
    client.find_one.return_value = _get_project(project_id)
    client.find.side_effect = [asset, [], tasks]

    # Act
    actual = sut.get_hierarchy_by_project(project_id, client)
    # Assert
    assert_that(
        set([x["_id"] for x in actual if x["type"] == "Task"])
    ).is_length(task_num)
