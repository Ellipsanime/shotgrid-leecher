from bson import ObjectId

from shotgrid_leecher.record.avalon_structures import AvalonProjectData
from shotgrid_leecher.record.intermediate_structures import IntermediateParams
from shotgrid_leecher.utils.collections import drop_keys

PROJECT_ID = "Project_564e3805"

_PROJ_DATA = IntermediateParams(
    **drop_keys(
        {"library_project"},
        AvalonProjectData().to_dict(),
    )
)

AVALON_DATA = [
    {
        "_id": ObjectId("614b3e4214dbac102817bb1b"),
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
        "_id": ObjectId("614b3e4214dbac102817bb1c"),
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
        "parent": "614b3e4214dbac102817bb1b",
    },
    {
        "_id": ObjectId("614b3e4214dbac102817bb1d"),
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
            "visualParent": "614b3e4214dbac102817bb1c",
            "tasks": None,
            "parents": ["Asset"],
        },
        "schema": "openpype:project-3.0",
        "parent": "614b3e4214dbac102817bb1b",
    },
    {
        "_id": ObjectId("614b3e4214dbac102817bb1e"),
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
            "visualParent": "614b3e4214dbac102817bb1d",
            "tasks": None,
            "parents": ["Asset", "PRP"],
        },
        "schema": "openpype:project-3.0",
        "parent": "614b3e4214dbac102817bb1b",
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
        "parent": ",Project_564e3805,",
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "PRP",
        "type": "Group",
        "parent": ",Project_564e3805,Asset,",
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Knife",
        "src_id": 23549,
        "type": "Asset",
        "parent": ",Project_564e3805,Asset,PRP,",
        "params": _PROJ_DATA.to_dict(),
    },
]
INTERMEDIATE_DB_DATA = [
    {
        "_id": PROJECT_ID,
        "src_id": 111,
        "type": "Project",
        "code": "Project",
        "parent": None,
        "object_id": ObjectId("614b3e4214dbac102817bb1b"),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Asset",
        "type": "Group",
        "parent": ",Project_564e3805,",
        "object_id": ObjectId("614b3e4214dbac102817bb1c"),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "PRP",
        "type": "Group",
        "parent": ",Project_564e3805,Asset,",
        "object_id": ObjectId("614b3e4214dbac102817bb1d"),
        "params": _PROJ_DATA.to_dict(),
    },
    {
        "_id": "Fork",
        "src_id": 23549,
        "type": "Asset",
        "parent": ",Project_564e3805,Asset,PRP,",
        "object_id": ObjectId("614b3e4214dbac102817bb1e"),
        "params": _PROJ_DATA.to_dict(),
    },
]
