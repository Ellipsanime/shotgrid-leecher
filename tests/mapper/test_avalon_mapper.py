import random
import uuid
from functools import partial
from typing import List

import attr
from assertpy import assert_that

from shotgrid_leecher.mapper.avalon_mapper import shotgrid_to_avalon
from shotgrid_leecher.record.avalon_structures import AvalonProjectData
from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.record.intermediate_structures import (
    IntermediateProject,
    IntermediateParams,
    IntermediateAsset,
    IntermediateTask,
    IntermediateShot,
    IntermediateEpisode,
    IntermediateRow,
    IntermediateSequence,
    IntermediateGroup,
    IntermediateProjectConfig,
)

TASK_NAMES = ["lines", "color", "look", "dev"]
STEP_NAMES = ["modeling", "shading", "rigging"]


def _get_project() -> IntermediateProject:
    project_id = str(uuid.uuid4())[0:8]
    return IntermediateProject(
        id=f"Project_{project_id}",
        src_id=111,
        params=_params(),
        code="",
        config=IntermediateProjectConfig(),
    )


def _params() -> IntermediateParams:
    common = set(attr.fields_dict(IntermediateParams).keys()).intersection(
        set(attr.fields_dict(AvalonProjectData).keys())
    )
    params = {
        k: v for k, v in AvalonProjectData().to_dict().items() if k in common
    }
    return IntermediateParams(**params)


def _get_asset_group(project: IntermediateProject) -> IntermediateGroup:
    return IntermediateGroup(
        id=ShotgridType.ASSET.value,
        parent=f",{project.id},",
        params=_params(),
    )


def _get_shot_group(project: IntermediateProject) -> IntermediateGroup:
    return IntermediateGroup(
        id=ShotgridType.GROUP.value,
        parent=f",{project.id},",
        params=_params(),
    )


def _get_prp_assets(
    parent: IntermediateRow,
) -> List[IntermediateGroup]:
    return [
        IntermediateGroup(
            id="PRP",
            parent=f"{parent.parent}{parent.id},",
            params=_params(),
        ),
        IntermediateAsset(
            id="Fork",
            parent=f"{parent.parent}{parent.id},PRP,",
            src_id=uuid.uuid4().int,
            params=_params(),
        ),
    ]


def _get_prp_asset_with_tasks(
    parent: IntermediateRow, task_num
) -> List[IntermediateTask]:
    asset = _get_prp_assets(parent)
    tasks = [
        IntermediateTask(
            id=f"{random.choice(TASK_NAMES)}_{uuid.uuid4().int}",
            src_id=uuid.uuid4().int,
            task_type=random.choice(STEP_NAMES),
            parent=f"{asset[1].parent}{asset[1].id},",
            params=_params(),
        )
        for _ in range(task_num)
    ]
    return [*asset, *tasks]


def _get_ep_with_shot(parent: IntermediateRow) -> List[IntermediateRow]:
    ep_name = f"ep{uuid.uuid4()}"
    sh_name = f"sh{uuid.uuid4()}"
    return [
        IntermediateEpisode(
            id=ep_name,
            src_id=uuid.uuid4().int,
            parent=f"{parent.parent}{parent.id},",
            params=_params(),
        ),
        IntermediateShot(
            id=sh_name,
            src_id=uuid.uuid4().int,
            parent=f"{parent.parent}{parent.id},{ep_name},",
            params=_params(),
        ),
    ]


def _get_seq_with_shot(parent: IntermediateRow) -> List[IntermediateRow]:
    seq_name = f"sq{uuid.uuid4()}"
    sh_name = f"sh{uuid.uuid4()}"
    return [
        IntermediateSequence(
            id=seq_name,
            src_id=uuid.uuid4().int,
            parent=f"{parent.parent}{parent.id},",
            params=_params(),
        ),
        IntermediateShot(
            id=sh_name,
            src_id=uuid.uuid4().int,
            parent=f"{parent.parent}{parent.id},{seq_name},",
            params=_params(),
        ),
    ]


def _get_ep_with_seq_with_shot(
    parent: IntermediateRow,
) -> List[IntermediateRow]:
    ep_name = f"ep{uuid.uuid4()}"
    seq_name = f"sq{uuid.uuid4()}"
    sh_name = f"sh{uuid.uuid4()}"
    return [
        IntermediateEpisode(
            id=ep_name,
            src_id=uuid.uuid4().int,
            parent=f"{parent.parent}{parent.id},",
            params=_params(),
        ),
        IntermediateSequence(
            id=seq_name,
            src_id=uuid.uuid4().int,
            parent=f"{parent.parent}{parent.id},{ep_name},",
            params=_params(),
        ),
        IntermediateShot(
            id=sh_name,
            src_id=uuid.uuid4().int,
            parent=f"{parent.parent}{parent.id},{ep_name},{seq_name},",
            params=_params(),
        ),
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
    assert_that(actual).contains_key(data[0].id)


def test_shotgrid_to_avalon_assets():
    # Arrange
    project = _get_project()
    asset_grp = _get_asset_group(project)
    data = [project, asset_grp, *_get_prp_assets(asset_grp)]

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual).is_length(4)


def test_shotgrid_to_avalon_assets_hierarchy():
    # Arrange
    project = _get_project()
    asset_grp = _get_asset_group(project)
    data = [project, asset_grp, *_get_prp_assets(asset_grp)]

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual).contains_only(*[x.id for x in data])
    assert_that(actual[asset_grp.id]["parent"]).is_equal_to(project.id)
    assert_that(actual[data[2].id]["parent"]).is_equal_to(project.id)
    assert_that(actual[data[3].id]["parent"]).is_equal_to(project.id)
    assert_that(actual[asset_grp.id]["data"]["visualParent"]).is_equal_to(None)
    assert_that(actual[data[2].id]["data"]["visualParent"]).is_equal_to(
        asset_grp.id
    )
    assert_that(actual[data[3].id]["data"]["visualParent"]).is_equal_to(
        data[2].id
    )


def test_shotgrid_to_avalon_assets_with_tasks():
    # Arrange
    match = partial(filter, lambda x: "_" not in x)
    project = _get_project()
    asset_grp = _get_asset_group(project)
    data = [project, asset_grp, *_get_prp_asset_with_tasks(asset_grp, 3)]

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual).is_length(4)
    assert_that(match(actual["Fork"]["data"]["tasks"].keys())).is_subset_of(
        set(TASK_NAMES)
    )


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
    steps = set([x.task_type for x in data[4:]])

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual[project.id]["config"]["tasks"]).is_length(len(steps))
    assert_that(actual[data[3].id]["data"]["tasks"]).is_length(task_num)


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
    assert_that(actual).contains_only(*[x.id for x in data])
    assert_that(
        [actual[k]["parent"] for k in actual.keys() if "parent" in actual[k]]
    ).contains_only(project.id)
    assert_that(actual[shot_grp.id]["data"]["visualParent"]).is_equal_to(None)
    assert_that(actual[data[2].id]["data"]["visualParent"]).is_equal_to(
        shot_grp.id
    )
    assert_that(actual[data[3].id]["data"]["visualParent"]).is_equal_to(
        data[2].id
    )
    assert_that(actual[data[4].id]["data"]["visualParent"]).is_equal_to(
        shot_grp.id
    )
    assert_that(actual[data[5].id]["data"]["visualParent"]).is_equal_to(
        data[4].id
    )
    assert_that(actual[data[6].id]["data"]["visualParent"]).is_equal_to(
        shot_grp.id
    )
    assert_that(actual[data[7].id]["data"]["visualParent"]).is_equal_to(
        data[6].id
    )
    assert_that(actual[data[8].id]["data"]["visualParent"]).is_equal_to(
        data[7].id
    )
