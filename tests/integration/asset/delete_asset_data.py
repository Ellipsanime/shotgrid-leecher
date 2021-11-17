from typing import Dict, Any

from bson import ObjectId

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

PROJECT_ID = "Project_2ffc00ab4"

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
        "_id": ObjectId("614b46d27f4b49b1ae47eed6"),
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
        "_id": ObjectId("614b46d27f4b49b1ae47eed7"),
        "type": "asset",
        "name": "Asset",
        "data": {
            **_DEF_DATA,
            "visualParent": None,
            "parents": [],
        },
        "schema": "openpype:project-3.0",
        "parent": ObjectId("614b46d27f4b49b1ae47eed6"),
    },
    {
        "_id": ObjectId("614b46d27f4b49b1ae47eed8"),
        "type": "asset",
        "name": "PRP",
        "data": {
            **_DEF_DATA,
            "visualParent": "614b46d27f4b49b1ae47eed7",
            "parents": ["Asset"],
        },
        "schema": "openpype:project-3.0",
        "parent": ObjectId("614b46d27f4b49b1ae47eed6"),
    },
    {
        "_id": ObjectId("614b46d27f4b49b1ae47eed9"),
        "type": "asset",
        "name": "Fork",
        "data": {
            **_DEF_DATA,
            "visualParent": "614b46d27f4b49b1ae47eed8",
            "parents": ["Asset", "PRP"],
        },
        "schema": "openpype:project-3.0",
        "parent": ObjectId("614b46d27f4b49b1ae47eed6"),
    },
    {
        "_id": ObjectId("614b46d27f4b49b1ae47ee10"),
        "type": "asset",
        "name": "Knife",
        "data": {
            **_DEF_DATA,
            "visualParent": "614b46d27f4b49b1ae47eed8",
            "parents": ["Asset", "PRP"],
        },
        "schema": "openpype:project-3.0",
        "parent": ObjectId("614b46d27f4b49b1ae47eed6"),
    },
    {
        "_id": ObjectId("614b46d27f4b49b1ae47ee11"),
        "type": "asset",
        "name": "Dagger",
        "data": {
            **_DEF_DATA,
            "visualParent": "614b46d27f4b49b1ae47ee10",
            "parents": ["Asset", "PRP"],
        },
        "schema": "openpype:project-3.0",
        "parent": ObjectId("614b46d27f4b49b1ae47eed6"),
    },
]
SHOTGRID_DATA = [
    IntermediateProject(
        id=PROJECT_ID,
        src_id=111,
        params=_PROJ_DATA,
        code="",
        config=IntermediateProjectConfig(),
    ),
    IntermediateGroup(
        id=ShotgridType.ASSET.value,
        parent=f",{PROJECT_ID},",
        params=_PROJ_DATA,
    ),
    IntermediateGroup(
        id="PRP",
        parent=f",{PROJECT_ID},Asset,",
        params=_PROJ_DATA,
    ),
    IntermediateAsset(
        id="Fork",
        src_id=50711,
        parent=f",{PROJECT_ID},Asset,PRP,",
        params=_PROJ_DATA,
    ),
]
INTERMEDIATE_DB_DATA = [
    {
        "_id": PROJECT_ID,
        "src_id": 111,
        "code": "Project",
        "type": "Project",
        "parent": None,
        "object_id": ObjectId("614b46d27f4b49b1ae47eed6"),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Asset",
        "type": "Group",
        "parent": f",{PROJECT_ID},",
        "object_id": ObjectId("614b46d27f4b49b1ae47eed7"),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "PRP",
        "type": "Group",
        "parent": f",{PROJECT_ID},Asset,",
        "object_id": ObjectId("614b46d27f4b49b1ae47eed8"),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Fork",
        "src_id": 50711,
        "type": "Asset",
        "parent": f",{PROJECT_ID},Asset,PRP,",
        "object_id": ObjectId("614b46d27f4b49b1ae47eed9"),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Knife",
        "src_id": 50712,
        "type": "Asset",
        "parent": f",{PROJECT_ID},Asset,PRP,",
        "object_id": ObjectId("614b46d27f4b49b1ae47ee10"),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Dagger",
        "src_id": 50713,
        "type": "Asset",
        "parent": f",{PROJECT_ID},Asset,PRP,Knife,",
        "object_id": ObjectId("614b46d27f4b49b1ae47ee11"),
        "params": _PROJ_DATA.to_dict(),
    },
]
