import uuid
from typing import Dict, Any

from shotgrid_leecher.record.avalon_structures import AvalonProjectData
from shotgrid_leecher.record.enums import ShotgridType
from shotgrid_leecher.record.intermediate_structures import (
    IntermediateProject,
    IntermediateParams,
    IntermediateAsset,
    IntermediateGroup,
    IntermediateProjectConfig,
)
from shotgrid_leecher.utils.collections import drop_keys
from shotgrid_leecher.utils.ids import to_object_id

PROJECT_ID = "Project_2ffc00ab4"
_SRC_ID = 111

_DEF_DATA: Dict[str, Any] = {
    "clipIn": 1,
    "clipOut": 1,
    "fps": 25.0,
    "frameEnd": 0,
    "frameStart": 0,
    "handleEnd": 0,
    "handleStart": 0,
    "pixelAspect": 0,
    "resolutionHeight": 0,
    "resolutionWidth": 0,
    "tools_env": [],
    "parent": [],
    "tasks": None,
}

_PROJ_DATA = IntermediateParams(
    **drop_keys(
        {"library_project"},
        AvalonProjectData.from_dict(_DEF_DATA).to_dict(),
    )
)

AVALON_DATA = [
    {
        "_id": to_object_id(_SRC_ID),
        "type": "project",
        "name": PROJECT_ID,
        "data": {
            "clipIn": 1,
            "clipOut": 1,
            "fps": 25.0,
            "frameEnd": 0,
            "frameStart": 0,
            "handleEnd": 0,
            "handleStart": 0,
            "pixelAspect": 0,
            "resolutionHeight": 0,
            "resolutionWidth": 0,
            "tools_env": [],
            "code": "",
            "visualParent": None,
            "library_project": False,
        },
        "schema": "openpype:project-3.0",
        "config": {"tasks": None},
        "parent": None,
    },
    {
        "_id": to_object_id(ShotgridType.ASSET.value),
        "type": "asset",
        "name": ShotgridType.ASSET.value,
        "data": {
            **_DEF_DATA,
            "visualParent": None,
            "parents": [],
        },
        "schema": "openpype:project-3.0",
        "parent": to_object_id(_SRC_ID),
    },
    {
        "_id": to_object_id("PRP"),
        "type": "asset",
        "name": "PRP",
        "data": {
            **_DEF_DATA,
            "visualParent": "614b46d27f4b49b1ae47eed7",
            "parents": [ShotgridType.ASSET.value],
        },
        "schema": "openpype:project-3.0",
        "parent": to_object_id(_SRC_ID),
    },
    {
        "_id": to_object_id(50711),
        "type": "asset",
        "name": "Fork",
        "data": {
            **_DEF_DATA,
            "visualParent": "614b46d27f4b49b1ae47eed8",
            "parents": [ShotgridType.ASSET.value, "PRP"],
        },
        "schema": "openpype:project-3.0",
        "parent": to_object_id(_SRC_ID),
    },
    {
        "_id": to_object_id(50712),
        "type": "asset",
        "name": "Knife",
        "data": {
            **_DEF_DATA,
            "visualParent": "614b46d27f4b49b1ae47eed8",
            "parents": [ShotgridType.ASSET.value, "PRP"],
        },
        "schema": "openpype:project-3.0",
        "parent": to_object_id(_SRC_ID),
    },
    {
        "_id": to_object_id(50713),
        "type": "asset",
        "name": "Dagger",
        "data": {
            **_DEF_DATA,
            "visualParent": "614b46d27f4b49b1ae47ee10",
            "parents": [ShotgridType.ASSET.value, "PRP"],
        },
        "schema": "openpype:project-3.0",
        "parent": to_object_id(_SRC_ID),
    },
]
SHOTGRID_DATA = [
    IntermediateProject(
        id=PROJECT_ID,
        src_id=111,
        params=_PROJ_DATA,
        code="",
        config=IntermediateProjectConfig(),
        object_id=to_object_id(_SRC_ID),
    ),
    IntermediateGroup(
        id=ShotgridType.ASSET.value,
        parent=f",{PROJECT_ID},",
        params=_PROJ_DATA,
        object_id=to_object_id(ShotgridType.ASSET.value),
    ),
    IntermediateGroup(
        id="PRP",
        parent=f",{PROJECT_ID},Assets,",
        params=_PROJ_DATA,
        object_id=to_object_id("PRP"),
    ),
    IntermediateAsset(
        id="Fork",
        src_id=50711,
        parent=f",{PROJECT_ID},Assets,PRP,",
        params=_PROJ_DATA,
        linked_entities=[],
        object_id=to_object_id(50711),
        status=str(uuid.uuid4()),
    ),
]
INTERMEDIATE_DB_DATA = [
    {
        "_id": PROJECT_ID,
        "src_id": 111,
        "code": "Project",
        "type": "Project",
        "parent": None,
        "object_id": to_object_id(_SRC_ID),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": ShotgridType.ASSET.value,
        "type": "Group",
        "parent": f",{PROJECT_ID},",
        "object_id": to_object_id(ShotgridType.ASSET.value),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "PRP",
        "type": "Group",
        "parent": f",{PROJECT_ID},Assets,",
        "object_id": to_object_id("PRP"),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Fork",
        "src_id": 50711,
        "type": ShotgridType.ASSET.value,
        "parent": f",{PROJECT_ID},Assets,PRP,",
        "object_id": to_object_id(50711),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Knife",
        "src_id": 50712,
        "type": ShotgridType.ASSET.value,
        "parent": f",{PROJECT_ID},Assets,PRP,",
        "object_id": to_object_id(50712),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Dagger",
        "src_id": 50713,
        "type": ShotgridType.ASSET.value,
        "parent": f",{PROJECT_ID},Assets,PRP,Knife,",
        "object_id": to_object_id(50713),
        "params": _PROJ_DATA.to_dict(),
    },
]
SHOTGRID_ASSET_TO_ASSET_LINKS = []
SHOTGRID_SHOT_TO_SHOT_LINKS = []
SHOTGRID_ASSET_TO_SHOT_LINKS = []
