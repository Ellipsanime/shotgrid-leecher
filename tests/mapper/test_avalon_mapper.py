import random
import uuid

from assertpy import assert_that

from shotgrid_leecher.mapper.avalon_mapper import shotgrid_to_avalon

TASK_NAMES = ["lines", "color", "look", "dev"]
STEP_NAMES = ["modeling", "shading", "rigging"]


def _get_project():

    project_id = str(uuid.uuid4())[0:8]
    return {
        "_id": f"Project_{project_id}",
        "src_id": 111,
        "type": "Project",
        "parent": None,
    }


def _get_asset_group(project):

    return {"_id": "Asset", "type": "Group", "parent": f",{project['_id']},"}


def _get_shot_group(project):

    return {"_id": "Shot", "type": "Group", "parent": f",{project['_id']},"}


def _get_prp_asset(parent):
    return [
        {
            "_id": "PRP",
            "type": "Group",
            "parent": f"{parent['parent']}{parent['_id']},",
        },
        {
            "_id": "Fork",
            "src_id": uuid.uuid4().int,
            "type": "Asset",
            "parent": f"{parent['parent']}{parent['_id']},PRP,",
        },
    ]


def _get_prp_asset_with_tasks(parent, task_num):
    asset = _get_prp_asset(parent)
    tasks = [
        {
            "_id": f"{random.choice(TASK_NAMES)}_{uuid.uuid4().int}",
            "src_id": uuid.uuid4().int,
            "type": "Task",
            "task_type": random.choice(STEP_NAMES),
            "parent": f"{asset[1]['parent']}{asset[1]['_id']},",
        }
        for i in range(task_num)
    ]
    return [*asset, *tasks]


def _get_ep_with_shot(parent):
    ep_name = f"ep{uuid.uuid4()}"
    sh_name = f"sh{uuid.uuid4()}"
    return [
        {
            "_id": ep_name,
            "src_id": uuid.uuid4().int,
            "type": "Episode",
            "parent": f"{parent['parent']}{parent['_id']},",
        },
        {
            "_id": sh_name,
            "src_id": uuid.uuid4().int,
            "type": "Shot",
            "parent": f"{parent['parent']}{parent['_id']},{ep_name},",
        },
    ]


def _get_seq_with_shot(parent):
    seq_name = f"sq{uuid.uuid4()}"
    sh_name = f"sh{uuid.uuid4()}"
    return [
        {
            "_id": seq_name,
            "src_id": uuid.uuid4().int,
            "type": "Sequence",
            "parent": f"{parent['parent']}{parent['_id']},",
        },
        {
            "_id": sh_name,
            "src_id": uuid.uuid4().int,
            "type": "Shot",
            "parent": f"{parent['parent']}{parent['_id']},{seq_name},",
        },
    ]


def _get_ep_with_seq_with_shot(parent):
    ep_name = f"ep{uuid.uuid4()}"
    seq_name = f"sq{uuid.uuid4()}"
    sh_name = f"sh{uuid.uuid4()}"
    return [
        {
            "_id": ep_name,
            "src_id": uuid.uuid4().int,
            "type": "Episode",
            "parent": f"{parent['parent']}{parent['_id']},",
        },
        {
            "_id": seq_name,
            "src_id": uuid.uuid4().int,
            "type": "Sequence",
            "parent": f"{parent['parent']}{parent['_id']},{ep_name},",
        },
        {
            "_id": sh_name,
            "src_id": uuid.uuid4().int,
            "type": "Shot",
            "parent": f"{parent['parent']}{parent['_id']},{ep_name},{seq_name},",
        },
    ]


def test_shotgrid_to_avalon_empty_list():
    # Arrange
    data = []

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual).is_equal_to({})


def test_shotgrid_to_avalon_project():
    # Arrange
    data = [_get_project()]

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual).is_length(1)
    assert_that(actual).contains_key(data[0]["_id"])


def test_shotgrid_to_avalon_assets():
    # Arrange
    project = _get_project()
    asset_grp = _get_asset_group(project)
    data = [project, asset_grp, *_get_prp_asset(asset_grp)]

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual).is_length(4)


def test_shotgrid_to_avalon_assets_hierarchy():
    # Arrange
    project = _get_project()
    asset_grp = _get_asset_group(project)
    data = [project, asset_grp, *_get_prp_asset(asset_grp)]

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual).contains_only(*[x["_id"] for x in data])
    assert_that(actual[asset_grp["_id"]]["parent"]).is_equal_to(project["_id"])
    assert_that(actual[data[2]["_id"]]["parent"]).is_equal_to(project["_id"])
    assert_that(actual[data[3]["_id"]]["parent"]).is_equal_to(project["_id"])
    assert_that(actual[asset_grp["_id"]]["data"]["visualParent"]).is_equal_to(
        None
    )
    assert_that(actual[data[2]["_id"]]["data"]["visualParent"]).is_equal_to(
        asset_grp["_id"]
    )
    assert_that(actual[data[3]["_id"]]["data"]["visualParent"]).is_equal_to(
        data[2]["_id"]
    )


def test_shotgrid_to_avalon_assets_with_tasks():
    # Arrange
    project = _get_project()
    asset_grp = _get_asset_group(project)
    data = [project, asset_grp, *_get_prp_asset_with_tasks(asset_grp, 3)]

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual).is_length(4)


def test_shotgrid_to_avalon_assets_with_tasks_values():
    # Arrange
    task_num = 3
    project = _get_project()
    asset_grp = _get_asset_group(project)
    data = [
        project,
        asset_grp,
        *_get_prp_asset_with_tasks(asset_grp, task_num),
    ]
    steps = set([x["task_type"] for x in data[4:]])

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual[project["_id"]]["config"]["tasks"]).is_length(
        len(steps)
    )
    assert_that(actual[data[3]["_id"]]["data"]["tasks"]).is_length(task_num)


def test_shotgrid_to_avalon_shots():
    # Arrange
    project = _get_project()
    shot_grp = _get_shot_group(project)
    data = [
        project,
        shot_grp,
        *_get_ep_with_shot(shot_grp),
        *_get_seq_with_shot(shot_grp),
        *_get_ep_with_seq_with_shot(shot_grp),
    ]

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual).is_length(9)


def test_shotgrid_to_avalon_shots_hierarchy():
    # Arrange
    project = _get_project()
    shot_grp = _get_shot_group(project)
    data = [
        project,
        shot_grp,
        *_get_ep_with_shot(shot_grp),
        *_get_seq_with_shot(shot_grp),
        *_get_ep_with_seq_with_shot(shot_grp),
    ]

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual).contains_only(*[x["_id"] for x in data])
    assert_that(
        [actual[k]["parent"] for k in actual.keys() if "parent" in actual[k]]
    ).contains_only(project["_id"])
    assert_that(actual[shot_grp["_id"]]["data"]["visualParent"]).is_equal_to(
        None
    )
    assert_that(actual[data[2]["_id"]]["data"]["visualParent"]).is_equal_to(
        shot_grp["_id"]
    )
    assert_that(actual[data[3]["_id"]]["data"]["visualParent"]).is_equal_to(
        data[2]["_id"]
    )
    assert_that(actual[data[4]["_id"]]["data"]["visualParent"]).is_equal_to(
        shot_grp["_id"]
    )
    assert_that(actual[data[5]["_id"]]["data"]["visualParent"]).is_equal_to(
        data[4]["_id"]
    )
    assert_that(actual[data[6]["_id"]]["data"]["visualParent"]).is_equal_to(
        shot_grp["_id"]
    )
    assert_that(actual[data[7]["_id"]]["data"]["visualParent"]).is_equal_to(
        data[6]["_id"]
    )
    assert_that(actual[data[8]["_id"]]["data"]["visualParent"]).is_equal_to(
        data[7]["_id"]
    )
