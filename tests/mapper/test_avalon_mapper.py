import random
import uuid
from functools import partial
from typing import List

import attr
from assertpy import assert_that

from shotgrid_leecher.mapper import intermediate_mapper
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
    IntermediateProjectStep,
)
from shotgrid_leecher.utils.ids import to_object_id

TASK_NAMES = ["lines", "color", "look", "dev"]
STEP_NAMES = ["modeling", "shading", "rigging"]


def _get_project() -> IntermediateProject:
    project_id = str(uuid.uuid4())[0:8]
    return IntermediateProject(
        id=f"Project_{project_id}",
        src_id=111,
        params=_params(),
        code="",
        config=IntermediateProjectConfig(
            steps=[IntermediateProjectStep(x, x[:1]) for x in STEP_NAMES]
        ),
        object_id=to_object_id(111),
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
        object_id=to_object_id(ShotgridType.ASSET.value),
    )


def _get_shot_group(project: IntermediateProject) -> IntermediateGroup:
    return IntermediateGroup(
        id=ShotgridType.GROUP.value,
        parent=f",{project.id},",
        params=_params(),
        object_id=to_object_id(ShotgridType.GROUP.value),
        parent_id=to_object_id(project.src_id),
    )


def _get_prp_assets(
    parent: IntermediateRow,
) -> List[IntermediateGroup]:
    return [
        IntermediateGroup(
            id="PRP",
            parent=f"{parent.parent}{parent.id},",
            params=_params(),
            object_id=to_object_id("PRP"),
        ),
        IntermediateAsset(
            id="Fork",
            parent=f"{parent.parent}{parent.id},PRP,",
            src_id=uuid.uuid4().int,
            params=_params(),
            linked_entities=[],
            object_id=to_object_id("Fork"),
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
            object_id=to_object_id(uuid.uuid4().int),
            parent_id=asset[1].object_id,
            status=str(uuid.uuid4()),
            assigned_users=[],
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
            object_id=to_object_id(ep_name),
        ),
        IntermediateShot(
            id=sh_name,
            src_id=uuid.uuid4().int,
            parent=f"{parent.parent}{parent.id},{ep_name},",
            params=_params(),
            linked_entities=[],
            object_id=to_object_id(sh_name),
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
            object_id=to_object_id(seq_name),
        ),
        IntermediateShot(
            id=sh_name,
            src_id=uuid.uuid4().int,
            parent=f"{parent.parent}{parent.id},{seq_name},",
            params=_params(),
            linked_entities=[],
            object_id=to_object_id(sh_name),
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
            object_id=to_object_id(ep_name),
        ),
        IntermediateSequence(
            id=seq_name,
            src_id=uuid.uuid4().int,
            parent=f"{parent.parent}{parent.id},{ep_name},",
            params=_params(),
            object_id=to_object_id(seq_name),
        ),
        IntermediateShot(
            id=sh_name,
            src_id=uuid.uuid4().int,
            parent=f"{parent.parent}{parent.id},{ep_name},{seq_name},",
            params=_params(),
            linked_entities=[],
            object_id=to_object_id(sh_name),
        ),
    ]


def test_shotgrid_to_avalon_empty_list():
    # Arrange
    data = []

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual).is_equal_to([])


def test_shotgrid_to_avalon_project():
    # Arrange
    data = [_get_project()]

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual).is_length(1)
    assert_that(actual[0]["name"]).is_equal_to(data[0].id)


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
    data = intermediate_mapper.map_parent_ids(
        [project, asset_grp, *_get_prp_assets(asset_grp)]
    )

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual[1]["parent"]).is_equal_to(project.object_id)
    assert_that(actual[2]["parent"]).is_equal_to(project.object_id)
    assert_that(actual[3]["parent"]).is_equal_to(project.object_id)
    assert_that(actual[1]["data"]["visualParent"]).is_none()
    assert_that(actual[2]["data"]["visualParent"]).is_equal_to(
        asset_grp.object_id
    )
    assert_that(actual[3]["data"]["visualParent"]).is_equal_to(
        data[2].object_id
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
    assert_that(match(actual[-1]["data"]["tasks"].keys())).is_subset_of(
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
    steps = list([x.task_type for x in data[4:]])

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual[0]["config"]["tasks"].keys()).is_length(len(steps))
    assert_that(actual[-1]["data"]["tasks"]).is_length(task_num)


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
    data = intermediate_mapper.map_parent_ids(
        [
            project,
            shot_grp,
            *_get_ep_with_shot(shot_grp),
            *_get_seq_with_shot(shot_grp),
            *_get_ep_with_seq_with_shot(shot_grp),
        ]
    )

    # Act
    actual = shotgrid_to_avalon(data)

    # Assert
    assert_that(actual).is_length(len(data))
    assert_that([k["parent"] for k in actual if "parent" in k]).contains_only(
        project.object_id
    )
    assert_that(actual[0]["data"]["visualParent"]).is_none()
    assert_that(actual[1]["data"]["visualParent"]).is_none()
    assert_that(actual[2]["data"]["visualParent"]).is_equal_to(
        shot_grp.object_id
    )
    assert_that(actual[3]["data"]["visualParent"]).is_equal_to(
        data[2].object_id
    )
    assert_that(actual[4]["data"]["visualParent"]).is_equal_to(
        shot_grp.object_id
    )
    assert_that(actual[5]["data"]["visualParent"]).is_equal_to(
        data[4].object_id
    )
    assert_that(actual[6]["data"]["visualParent"]).is_equal_to(
        shot_grp.object_id
    )
    assert_that(actual[7]["data"]["visualParent"]).is_equal_to(
        data[6].object_id
    )
    assert_that(actual[8]["data"]["visualParent"]).is_equal_to(
        data[7].object_id
    )
