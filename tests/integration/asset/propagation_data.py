import random
import uuid

from bson import ObjectId
from toolz import compose

from shotgrid_leecher.record.enums import ShotgridField

_RAND = random.randint

_I32 = compose(
    lambda x: x * 2 if x % 5 == 0 else x,
    lambda: _RAND(10 ** 2, 10 ** 10),
)


PROJECT_ID = f"Project_{str(uuid.uuid4())[:5]}"
AVALON_DATA = [
    {
        "_id": ObjectId(),
        "type": "project",
        "name": PROJECT_ID,
        "data": {
            "clipIn": _I32(),
            "clipOut": _I32(),
            "fps": float(_I32() / 3),
            "frameEnd": _I32(),
            "frameStart": _I32(),
            "handleEnd": _I32(),
            "handleStart": _I32(),
            "pixelAspect": _I32(),
            "resolutionHeight": _I32(),
            "resolutionWidth": _I32(),
            "tools_env": [_I32(), _I32(), _I32()],
            "code": PROJECT_ID,  # str(uuid.uuid4())[:5],
            "library_project": False,
            "visualParent": None,
            "parent": [],
            "tasks": None,
        },
        "schema": "openpype:project-3.0",
        "config": {"tasks": None},
        "parent": None,
    }
]
SHOTGRID_DATA_PROJECT = [
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "name": PROJECT_ID,
        "code": PROJECT_ID,
        "type": "Project",
    }
]
SHOTGRID_DATA_STEPS = [
    {"code": "modeling", "short_name": "m", "id": -3},
    {"code": "rigging", "short_name": "r", "id": -3},
    {"code": "render", "short_name": "re", "id": -3},
    {"code": "layout", "short_name": "l", "id": -3},
    {"code": "animation", "short_name": "a", "id": -3},
]
SHOTGRID_DATA_ASSETS = [
    {
        "type": "Asset",
        "code": "Fork1",
        "sg_asset_type": "MXB",
        "id": 11001,
        "tasks": [
            {
                "id": _RAND(10 ** 2, 10 ** 10),
                "name": "look",
                "type": "Task",
                "step": {"name": "modeling"},
                ShotgridField.ENTITY.value: {
                    "type": "Asset",
                    "name": "Fork1",
                    "id": 11001,
                },
            },
        ],
    }
]
SHOTGRID_DATA_SHOTS = [
    {
        "type": "Shot",
        "id": 110,
        "sequence": {"id": 1, "name": "SQ_1", "type": "Sequence"},
        "episode": {"id": 1, "name": "EP_1", "type": "Episode"},
        "code": "SHOT10",
        ShotgridField.SEQUENCE_EPISODE.value: {
            "id": 1,
            "name": "EP_1",
            "type": "Episode",
        },
        "sg_cut_in": _RAND(10 ** 2, 10 ** 10),
        "sg_cut_out": _I32() + 10,
    },
]
SHOTGRID_DATA_TASKS = [
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "color",
        "step": {"name": "render"},
        ShotgridField.ENTITY.value: {
            "type": "Shot",
            "name": "SHOT10",
            "id": 110,
        },
    },
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "dev",
        "step": {"name": "layout"},
        ShotgridField.ENTITY.value: {
            "type": "Shot",
            "name": "SHOT10",
            "id": 110,
        },
    },
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "rig",
        "step": {"name": "layout"},
        ShotgridField.ENTITY.value: {
            "type": "Shot",
            "name": "SHOT10",
            "id": 110,
        },
    },
]
