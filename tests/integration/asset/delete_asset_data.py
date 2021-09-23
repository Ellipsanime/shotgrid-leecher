from typing import Dict, Any

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

AVALON_DATA = [
    {
        "_id": "614b46d27f4b49b1ae47eed6",
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
        "_id": "614b46d27f4b49b1ae47eed7",
        "type": "asset",
        "name": "Asset",
        "data": {
            **_DEF_DATA,
            "visualParent": None,
            "parents": [],
        },
        "schema": "openpype:project-3.0",
        "parent": "614b46d27f4b49b1ae47eed6",
    },
    {
        "_id": "614b46d27f4b49b1ae47eed8",
        "type": "asset",
        "name": "PRP",
        "data": {
            **_DEF_DATA,
            "visualParent": "614b46d27f4b49b1ae47eed7",
            "parents": ["Asset"],
        },
        "schema": "openpype:project-3.0",
        "parent": "614b46d27f4b49b1ae47eed6",
    },
    {
        "_id": "614b46d27f4b49b1ae47eed9",
        "type": "asset",
        "name": "Fork",
        "data": {
            **_DEF_DATA,
            "visualParent": "614b46d27f4b49b1ae47eed8",
            "parents": ["Asset", "PRP"],
        },
        "schema": "openpype:project-3.0",
        "parent": "614b46d27f4b49b1ae47eed6",
    },
    {
        "_id": "614b46d27f4b49b1ae47ee10",
        "type": "asset",
        "name": "Knife",
        "data": {
            **_DEF_DATA,
            "visualParent": "614b46d27f4b49b1ae47eed8",
            "parents": ["Asset", "PRP"],
        },
        "schema": "openpype:project-3.0",
        "parent": "614b46d27f4b49b1ae47eed6",
    },
    {
        "_id": "614b46d27f4b49b1ae47ee11",
        "type": "asset",
        "name": "Dagger",
        "data": {
            **_DEF_DATA,
            "visualParent": "614b46d27f4b49b1ae47ee10",
            "parents": ["Asset", "PRP"],
        },
        "schema": "openpype:project-3.0",
        "parent": "614b46d27f4b49b1ae47eed6",
    },
]
SHOTGRID_DATA = [
    {
        "_id": PROJECT_ID,
        "src_id": 111,
        "type": "Project",
        "parent": None,
    },
    {
        "_id": "Asset",
        "type": "Group",
        "parent": f",{PROJECT_ID},",
    },
    {
        "_id": "PRP",
        "type": "Group",
        "parent": f",{PROJECT_ID},Asset,",
    },
    {
        "_id": "Fork",
        "src_id": 50711,
        "type": "Asset",
        "parent": f",{PROJECT_ID},Asset,PRP,",
    },
]
INTERMEDIATE_DB_DATA = [
    {
        "_id": PROJECT_ID,
        "src_id": 111,
        "type": "Project",
        "parent": None,
        "object_id": "614b46d27f4b49b1ae47eed6",
    },
    {
        "_id": "Asset",
        "type": "Group",
        "parent": f",{PROJECT_ID},",
        "object_id": "614b46d27f4b49b1ae47eed7",
    },
    {
        "_id": "PRP",
        "type": "Group",
        "parent": f",{PROJECT_ID},Asset,",
        "object_id": "614b46d27f4b49b1ae47eed8",
    },
    {
        "_id": "Fork",
        "src_id": 50711,
        "type": "Asset",
        "parent": f",{PROJECT_ID},Asset,PRP,",
        "object_id": "614b46d27f4b49b1ae47eed9",
    },
    {
        "_id": "Knife",
        "src_id": 50712,
        "type": "Asset",
        "parent": f",{PROJECT_ID},Asset,PRP,",
        "object_id": "614b46d27f4b49b1ae47ee10",
    },
    {
        "_id": "Dagger",
        "src_id": 50713,
        "type": "Asset",
        "parent": f",{PROJECT_ID},Asset,PRP,Knife,",
        "object_id": "614b46d27f4b49b1ae47ee11",
    },
]
