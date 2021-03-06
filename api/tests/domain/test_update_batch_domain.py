import random
import uuid
from typing import Any, Callable, List
from unittest.mock import Mock

import attr
from _pytest.monkeypatch import MonkeyPatch
from assertpy import assert_that
from mongomock import MongoClient

import shotgrid_leecher.repository.shotgrid_hierarchy_repo as repository
import shotgrid_leecher.utils.connectivity as conn
from shotgrid_leecher.domain import batch_domain as sut
from shotgrid_leecher.record.avalon_structures import AvalonProjectData
from shotgrid_leecher.record.commands import UpdateShotgridInAvalonCommand
from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.record.intermediate_structures import (
    IntermediateProject,
    IntermediateParams,
    IntermediateRow,
    IntermediateAsset,
    IntermediateTask,
    IntermediateGroup,
    IntermediateProjectConfig,
    IntermediateProjectStep,
)
from shotgrid_leecher.record.leecher_structures import ShotgridCredentials
from shotgrid_leecher.record.results import BatchResult
from shotgrid_leecher.record.shotgrid_subtypes import (
    FieldsMapping,
    ProjectFieldsMapping,
    AssetFieldsMapping,
    ShotFieldsMapping,
    TaskFieldsMapping,
    StepFieldsMapping,
    AssetToShotLinkMapping,
    ShotToShotLinkMapping,
    AssetToAssetLinkMapping,
)
from shotgrid_leecher.repository import intermediate_hierarchy_repo
from shotgrid_leecher.utils.ids import to_object_id
from shotgrid_leecher.writers import batch_writer

TASK_NAMES = ["lines", "color", "look", "dev"]
STEP_NAMES = ["modeling", "shading", "rigging"]


def _fun(param: Any) -> Callable[[Any], Any]:
    return lambda *_: param


def _params() -> IntermediateParams:
    common = set(attr.fields_dict(IntermediateParams).keys()).intersection(
        set(attr.fields_dict(AvalonProjectData).keys())
    )
    params = {
        k: v for k, v in AvalonProjectData().to_dict().items() if k in common
    }
    return IntermediateParams(**params)


def _patch_adjacent(patcher: MonkeyPatch, client, hierarchy: List) -> None:
    patcher.setattr(conn, "get_db_client", _fun(client))
    patcher.setattr(repository, "get_hierarchy_by_project", _fun(hierarchy))


def _default_fields_mapping() -> FieldsMapping:
    return FieldsMapping(
        ProjectFieldsMapping.from_dict({}),
        AssetFieldsMapping.from_dict({}),
        ShotFieldsMapping.from_dict({}),
        TaskFieldsMapping.from_dict({}),
        StepFieldsMapping.from_dict({}),
        AssetToShotLinkMapping.from_dict({}),
        ShotToShotLinkMapping.from_dict({}),
        AssetToAssetLinkMapping.from_dict({}),
    )


def _get_project() -> IntermediateProject:

    project_id = str(uuid.uuid4())[0:8]

    return IntermediateProject(
        id=f"Project_{project_id}",
        code=f"Project_{project_id}",
        src_id=111,
        params=_params(),
        config=IntermediateProjectConfig(
            steps=[IntermediateProjectStep(x, x[:1]) for x in STEP_NAMES]
        ),
        object_id=to_object_id(111),
    )


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
            object_id=to_object_id("Fork"),
            linked_entities=[],
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
            status=str(uuid.uuid4()),
            assigned_users=[],
        )
        for _ in range(task_num)
    ]
    return [*asset, *tasks]


def test_shotgrid_to_avalon_batch_update_empty(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    _patch_adjacent(monkeypatch, client, [])
    command = UpdateShotgridInAvalonCommand(
        123,
        "",
        True,
        ShotgridCredentials("", "", ""),
        _default_fields_mapping(),
        AvalonProjectData(),
    )

    # Act
    sut.update_shotgrid_in_avalon(command)

    # Assert
    assert_that(client["avalon"].list_collection_names()).is_length(0)


def test_shotgrid_to_avalon_batch_update_project(monkeypatch: MonkeyPatch):
    # Arrange
    client = Mock()
    data = [_get_project()]

    upsert_mock = Mock(return_value=data[0].object_id)
    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(
        intermediate_hierarchy_repo, "fetch_by_project", _fun(data)
    )
    monkeypatch.setattr(batch_writer, "overwrite_intermediate", _fun(None))
    monkeypatch.setattr(batch_writer, "upsert_avalon_rows", upsert_mock)

    command = UpdateShotgridInAvalonCommand(
        123,
        data[0].id,
        True,
        ShotgridCredentials("", "", ""),
        _default_fields_mapping(),
        AvalonProjectData(),
    )

    # Act
    sut.update_shotgrid_in_avalon(command)

    # Assert
    assert_that(upsert_mock.call_args).is_length(2)
    assert_that(upsert_mock.call_args_list).is_length(1)
    assert_that(upsert_mock.call_args_list[0][0][1][0]["_id"]).is_equal_to(
        data[0].object_id
    )


def test_shotgrid_to_avalon_batch_update_asset_value(monkeypatch: MonkeyPatch):
    # Arrange
    client = MongoClient()
    project = _get_project()
    asset_grp = _get_asset_group(project)
    data = [project, asset_grp, *_get_prp_assets(asset_grp)]
    call_list = []

    def upsert_mock(project_name, rows):
        for x in rows:
            call_list.append(x["_id"])

    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(
        intermediate_hierarchy_repo, "fetch_by_project", _fun(data)
    )
    monkeypatch.setattr(batch_writer, "overwrite_intermediate", _fun(None))
    monkeypatch.setattr(batch_writer, "upsert_avalon_rows", upsert_mock)

    command = UpdateShotgridInAvalonCommand(
        123,
        project.id,
        True,
        ShotgridCredentials("", "", ""),
        _default_fields_mapping(),
        AvalonProjectData(),
    )

    # Act
    sut.update_shotgrid_in_avalon(command)

    # Assert
    assert_that(call_list).is_length(4)
    assert_that(call_list[0]).is_equal_to(data[0].object_id)
    assert_that(call_list[1]).is_equal_to(data[1].object_id)


def test_shotgrid_to_avalon_batch_update_asset_hierarchy_db(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    client = MongoClient()
    project = _get_project()
    asset_grp = _get_asset_group(project)
    data = [project, asset_grp, *_get_prp_assets(asset_grp)]

    def upsert_mock(_, row):
        return row["_id"]

    insert_intermediate = Mock()

    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(
        intermediate_hierarchy_repo, "fetch_by_project", _fun(data)
    )
    monkeypatch.setattr(
        batch_writer, "overwrite_intermediate", insert_intermediate
    )
    monkeypatch.setattr(batch_writer, "upsert_avalon_row", upsert_mock)

    command = UpdateShotgridInAvalonCommand(
        123,
        project.id,
        True,
        ShotgridCredentials("", "", ""),
        _default_fields_mapping(),
        AvalonProjectData(),
    )

    # Act
    sut.update_shotgrid_in_avalon(command)

    # Assert
    assert_that(insert_intermediate.call_count).is_equal_to(1)
    assert_that(insert_intermediate.call_args_list[0][0][1]).is_type_of(list)
    assert_that(
        insert_intermediate.call_args_list[0][0][1][0].object_id
    ).is_equal_to(data[0].object_id)
    assert_that(
        insert_intermediate.call_args_list[0][0][1][1].object_id
    ).is_equal_to(data[1].object_id)
    assert_that(
        insert_intermediate.call_args_list[0][0][1][2].object_id
    ).is_not_none()
    assert_that(
        insert_intermediate.call_args_list[0][0][1][3].object_id
    ).is_not_none()


def test_shotgrid_to_avalon_batch_update_asset_with_tasks(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    client = MongoClient()
    project = _get_project()
    asset_grp = _get_asset_group(project)
    data = [project, asset_grp, *_get_prp_asset_with_tasks(asset_grp, 3)]
    call_list = []

    def upsert_mock(project_name, rows):
        for x in rows:
            call_list.append(x["_id"])

    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))
    monkeypatch.setattr(
        intermediate_hierarchy_repo, "fetch_by_project", _fun(data)
    )
    monkeypatch.setattr(batch_writer, "overwrite_intermediate", _fun(None))
    monkeypatch.setattr(batch_writer, "upsert_avalon_rows", upsert_mock)

    command = UpdateShotgridInAvalonCommand(
        123,
        project.id,
        True,
        ShotgridCredentials("", "", ""),
        _default_fields_mapping(),
        AvalonProjectData(),
    )

    # Act
    sut.update_shotgrid_in_avalon(command)

    # Assert
    assert_that(call_list).is_length(4)
    assert_that(call_list[0]).is_equal_to(data[0].object_id)


def test_shotgrid_to_avalon_batch_update_wrong_project_name(
    monkeypatch: MonkeyPatch,
):
    # Arrange
    client = MongoClient()
    data = [_get_project()]

    monkeypatch.setattr(conn, "get_db_client", _fun(client))
    monkeypatch.setattr(repository, "get_hierarchy_by_project", _fun(data))

    openpype_project_name = str(uuid.uuid4())[0:8]
    overwrite = bool(random.getrandbits(1))

    command = UpdateShotgridInAvalonCommand(
        123,
        openpype_project_name,
        overwrite,
        ShotgridCredentials("", "", ""),
        _default_fields_mapping(),
        AvalonProjectData(),
    )

    # Act
    res = sut.update_shotgrid_in_avalon(command)

    # Assert
    assert_that(res).is_equal_to(BatchResult.WRONG_PROJECT_NAME)
