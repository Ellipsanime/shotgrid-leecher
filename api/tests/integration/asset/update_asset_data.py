from record.avalon_structures import AvalonProjectData
from record.intermediate_structures import IntermediateParams
from utils.collections import drop_keys
from utils.ids import to_object_id

PROJECT_ID = "Project_8e19ffaa"

_PROJ_DATA = IntermediateParams(
    **drop_keys(
        {"library_project"},
        AvalonProjectData().to_dict(),
    )
)

AVALON_DATA = [
    {
        "_id": to_object_id(111),
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
            "library_project": False,
            "visualParent": None,
        },
        "schema": "openpype:project-3.0",
        "config": {"tasks": None},
        "parent": None,
    },
    {
        "_id": to_object_id("Asset"),
        "type": "asset",
        "name": "Asset",
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
            "parent": [],
            "visualParent": None,
            "tasks": None,
            "parents": [],
        },
        "schema": "openpype:project-3.0",
        "parent": to_object_id(111),
    },
    {
        "_id": to_object_id("PRP"),
        "type": "asset",
        "name": "PRP",
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
            "parent": [],
            "visualParent": "614b46d27f4b49b1ae47eed7",
            "tasks": None,
            "parents": ["Asset"],
        },
        "schema": "openpype:project-3.0",
        "parent": to_object_id(111),
    },
    {
        "_id": to_object_id(50711),
        "type": "asset",
        "name": "Fork",
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
            "parent": [],
            "visualParent": "614b46d27f4b49b1ae47eed8",
            "tasks": None,
            "parents": ["Asset", "PRP"],
        },
        "schema": "openpype:project-3.0",
        "parent": to_object_id(111),
    },
]
SHOTGRID_DATA = [
    {
        "_id": PROJECT_ID,
        "src_id": 111,
        "type": "Project",
        "code": "Project",
        "parent": None,
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Asset",
        "type": "Group",
        "parent": f",{PROJECT_ID},",
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "PROPS",
        "type": "Group",
        "parent": f",{PROJECT_ID},Asset,",
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Fork",
        "src_id": 50712,
        "type": "Asset",
        "parent": f",{PROJECT_ID},Asset,PROPS,",
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "PRP",
        "type": "Group",
        "parent": f",{PROJECT_ID},Asset,",
        "params": _PROJ_DATA.to_dict(),
    },
]
INTERMEDIATE_DB_DATA = [
    {
        "_id": PROJECT_ID,
        "src_id": 111,
        "code": "Project",
        "type": "Project",
        "parent": None,
        "object_id": to_object_id(111),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Asset",
        "type": "Group",
        "parent": f",{PROJECT_ID},",
        "object_id": to_object_id("Asset"),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "PRP",
        "type": "Group",
        "parent": f",{PROJECT_ID},Asset,",
        "object_id": to_object_id("PRP"),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Fork",
        "src_id": 50711,
        "type": "Asset",
        "parent": f",{PROJECT_ID},Asset,PRP,",
        "object_id": to_object_id(50711),
        "params": _PROJ_DATA.to_dict(),
    },
]
SHOTGRID_ASSET_TO_ASSET_LINKS = []
SHOTGRID_SHOT_TO_SHOT_LINKS = []
SHOTGRID_ASSET_TO_SHOT_LINKS = []
