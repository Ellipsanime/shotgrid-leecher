import random
import uuid
from typing import Dict, Any, List
from unittest.mock import PropertyMock

from assertpy import assert_that

from shotgrid_leecher.repository.utils.hierarchy_traversal import (
    ShotgridFindHierarchyTraversal,
)

_RAND = random.randint


def _get_project(id_: int) -> Dict[str, Any]:
    return {
        "Type": "Project",
        "id": id_,
        "code": f"Project_{str(uuid.uuid4())[-7:]}",
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


def test_shots_traversal():
    # Arrange
    tasks = _get_shot_tasks()
    shots = _get_shots()
    project_id = random.randint(10, 1000)
    client = PropertyMock()
    client.find_one.return_value = _get_project(project_id)
    client.find.side_effect = [[], shots, tasks]

    sut = ShotgridFindHierarchyTraversal(project_id, client)
    # Act
    actual = sut.traverse_from_the_top()
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

    sut = ShotgridFindHierarchyTraversal(project_id, client)
    # Act
    actual = sut.traverse_from_the_top()
    # Assert
    assert_that(actual).extracting(
        "type", filter={"parent": None}
    ).is_equal_to(["Project"])
    assert_that(actual).extracting(
        "type", filter={"parent": f",{project['code']},"}
    ).is_equal_to(["Group"])
    assert_that(actual).extracting(
        "type", filter={"parent": f",{project['code']},Shot,"}
    ).is_equal_to(["Shot", "Episode", "Sequence", "Episode"])
    assert_that(actual).extracting(
        "type", filter={"parent": f",{project['code']},Shot,EP_OF_SHOT2,"}
    ).is_equal_to(["Shot"])
    assert_that(actual).extracting(
        "type", filter={"parent": f",{project['code']},Shot,SQ_OF_SHOT3,"}
    ).is_equal_to(["Shot"])
    assert_that(actual).extracting(
        "type", filter={"parent": f",{project['code']},Shot,Empty1,"}
    ).is_equal_to(["Task"])
    assert_that(actual).extracting(
        "type", filter={"parent": f",{project['code']},Shot,EP_OF_SHOT4,"}
    ).is_equal_to(["Sequence"])
    assert_that(actual).extracting(
        "type",
        filter={"parent": f",{project['code']},Shot,EP_OF_SHOT4,SQ_OF_SHOT4,"},
    ).is_equal_to(["Shot"])
    assert_that(actual).extracting(
        "type",
        filter={"parent": f",{project['code']},Shot,EP_OF_SHOT2,SHOT2,"},
    ).is_equal_to(["Task"])
    assert_that(actual).extracting(
        "type",
        filter={"parent": f",{project['code']},Shot,SQ_OF_SHOT3,SHOT3,"},
    ).is_equal_to(["Task"])
    assert_that(actual).extracting(
        "type",
        filter={
            "parent": f",{project['code']},Shot,EP_OF_SHOT4,SQ_OF_SHOT4,SHOT4,"
        },
    ).is_equal_to(["Task"])


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

    sut = ShotgridFindHierarchyTraversal(project_id, client)
    # Act
    actual = sut.traverse_from_the_top()

    # Assert
    assert_that(actual).extracting(
        "type", filter={"parent": None}
    ).is_equal_to(["Project"])
    assert_that(actual).extracting(
        "type", filter={"parent": f",{project['code']},"}
    ).is_equal_to(["Group"])
    assert_that(actual).extracting(
        "type", filter={"parent": f",{project['code']},Asset,"}
    ).is_equal_to(["Group"])
    assert_that(actual).extracting(
        "type", filter={"parent": f",{project['code']},Asset,PRP,"}
    ).is_equal_to(["Asset"])
    assert_that(actual).extracting(
        "type",
        filter={"parent": f",{project['code']},Asset,PRP,{asset[0]['code']},"},
    ).is_equal_to(["Task", "Task"])


def test_assets_traversal():
    # Arrange
    task_num = 2
    tasks = _get_asset_tasks(task_num)
    asset = _get_simple_assets([x.get("id") for x in tasks])
    project_id = random.randint(10, 1000)
    client = PropertyMock()
    client.find_one.return_value = _get_project(project_id)
    client.find.side_effect = [asset, [], tasks]

    sut = ShotgridFindHierarchyTraversal(project_id, client)
    # Act
    actual = sut.traverse_from_the_top()
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

    sut = ShotgridFindHierarchyTraversal(project_id, client)
    # Act
    actual = sut.traverse_from_the_top()
    # Assert
    assert_that(
        set([x["_id"] for x in actual if x["type"] == "Task"])
    ).is_length(task_num)
