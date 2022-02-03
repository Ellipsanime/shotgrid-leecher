from record.avalon_structures import AvalonProjectData
from record.intermediate_structures import IntermediateParams
from utils.collections import drop_keys
from utils.ids import to_object_id

OVERWRITE_PROJECT_ID = "Project_bebc4f75"


_PROJ_DATA = IntermediateParams(
    **drop_keys(
        {"library_project"},
        AvalonProjectData().to_dict(),
    )
)

OVERWRITE_AVALON_DATA = [
    {
        "_id": to_object_id(111),
        "type": "project",
        "name": OVERWRITE_PROJECT_ID,
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
            "visualParent": "614ae8dfef6bfb71c7a5475b",
            "tasks": None,
            "parents": ["Asset"],
        },
        "schema": "openpype:project-3.0",
        "parent": to_object_id(111),
    },
    {
        "_id": to_object_id("Fork"),
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
            "visualParent": "614ae8dfef6bfb71c7a5475c",
            "tasks": None,
            "parents": ["Asset", "PRP"],
        },
        "schema": "openpype:project-3.0",
        "parent": to_object_id(111),
    },
]

OVERWRITE_SHOTGRID_DATA = [
    {
        "_id": OVERWRITE_PROJECT_ID,
        "src_id": 111,
        "type": "Project",
        "code": "Project",
        "parent": None,
        "params": _PROJ_DATA.to_dict(),
    }
]


OVERWRITE_INTERMEDIATE_DB_DATA = [
    {
        "_id": OVERWRITE_PROJECT_ID,
        "src_id": 111,
        "type": "Project",
        "code": "Project",
        "parent": None,
        "object_id": to_object_id(111),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Asset",
        "type": "Group",
        "parent": ",Project_bebc4f75,",
        "object_id": to_object_id("Asset"),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "PRP",
        "type": "Group",
        "parent": ",Project_bebc4f75,Asset,",
        "object_id": to_object_id("PRP"),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Fork",
        "src_id": 16284,
        "type": "Asset",
        "parent": ",Project_bebc4f75,Asset,PRP,",
        "object_id": to_object_id("Fork"),
        "params": _PROJ_DATA.to_dict(),
    },
]
