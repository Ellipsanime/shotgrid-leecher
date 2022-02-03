import random
import uuid

from toolz import compose

from record.enums import ShotgridField

_RAND = random.randint

_I32 = compose(
    lambda x: None if x % 5 == 0 else x,
    lambda: _RAND(10 ** 2, 10 ** 10),
)

PROJECT_ID = f"Project_{str(uuid.uuid4())[:5]}"

SHOTGRID_DATA_PROJECT = [
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "name": PROJECT_ID,
        "code": PROJECT_ID,
        "type": "Project",
    }
]
SHOTGRID_DATA_STEPS = [
    {"code": "modeling", "short_name": "m", "id": -1},
    {"code": "rigging", "short_name": "r", "id": -1},
    {"code": "render", "short_name": "re", "id": -1},
    {"code": "layout", "short_name": "l", "id": -1},
    {"code": "animation", "short_name": "a", "id": -1},
]
SHOTGRID_DATA_ASSETS = [
    {
        "type": "Asset",
        "code": "Orphan",
        "id": 11001,
        "tasks": [
            {
                "id": _RAND(10 ** 2, 10 ** 10),
                "sg_status_list": str(uuid.uuid4()),
                "name": "look",
                "type": "Task",
                "step": {"name": "modeling"},
                ShotgridField.ENTITY.value: {
                    "type": "Asset",
                    "name": "Orphan",
                    "id": 11001,
                },
            },
        ],
    }
]
SHOTGRID_DATA_SHOTS = []
SHOTGRID_DATA_TASKS = [
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "look",
        "step": {"name": "modeling"},
        "sg_status_list": str(uuid.uuid4()),
        ShotgridField.ENTITY.value: {
            "type": "Asset",
            "name": "Orphan",
            "id": 11001,
        },
    },
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "dev",
        "step": {"name": "rigging"},
        "sg_status_list": str(uuid.uuid4()),
        ShotgridField.ENTITY.value: {
            "type": "Asset",
            "name": "Orphan",
            "id": 11001,
        },
    },
]
SHOTGRID_ASSET_TO_ASSET_LINKS = []
SHOTGRID_SHOT_TO_SHOT_LINKS = []
SHOTGRID_ASSET_TO_SHOT_LINKS = []
