import random
import uuid

from shotgrid_leecher.record.enums import ShotgridType, ShotgridField

_RAND = random.randint

PROJECT_ID = "Project_53f5e90066de"

FIELD_PROJECT_ID = str(uuid.uuid4())
FIELD_ASSET_TYPE = str(uuid.uuid4())
FIELD_ASSET_ID = str(uuid.uuid4())
FIELD_SHOT_ID = str(uuid.uuid4())
FIELD_SHOT_SEQUENCE = f"sg_{str(uuid.uuid4())}"
FIELD_SHOT_EPISODE = f"sg_{str(uuid.uuid4())}"
FIELD_SHOT_SEQUENCE_EP = f"sg_{str(uuid.uuid4())}.{str(uuid.uuid4())}.episode"
FIELD_TASK_ID = str(uuid.uuid4())
FIELD_TASK_STEP = str(uuid.uuid4())
FIELD_TASK_ENTITY = str(uuid.uuid4())

FIELDS_MAPPING = {
    ShotgridType.PROJECT.value.lower(): {
        ShotgridField.ID.value: FIELD_PROJECT_ID,
    },
    ShotgridType.ASSET.value.lower(): {
        ShotgridField.ID.value: FIELD_ASSET_ID,
        ShotgridField.ASSET_TYPE.value: FIELD_ASSET_TYPE,
    },
    ShotgridType.SHOT.value.lower(): {
        ShotgridField.ID.value: FIELD_SHOT_ID,
        ShotgridField.SEQUENCE.value: FIELD_SHOT_SEQUENCE,
        ShotgridField.EPISODE.value: FIELD_SHOT_EPISODE,
        ShotgridField.SEQUENCE_EPISODE.value: FIELD_SHOT_SEQUENCE_EP,
    },
    ShotgridType.TASK.value.lower(): {
        ShotgridField.ID.value: FIELD_TASK_ID,
        ShotgridField.STEP.value: FIELD_TASK_STEP,
        ShotgridField.ENTITY.value: FIELD_TASK_ENTITY,
    },
}

SHOTGRID_DATA_PROJECT = [
    {
        FIELD_PROJECT_ID: _RAND(10 ** 2, 10 ** 10),
        "name": PROJECT_ID,
        "type": "Project",
        "code": PROJECT_ID,
    }
]
SHOTGRID_DATA_STEPS = [
    {"code": "modeling", "short_name": "m", "id": -2},
    {"code": "rigging", "short_name": "r", "id": -2},
    {"code": "render", "short_name": "re", "id": -2},
    {"code": "layout", "short_name": "l", "id": -2},
    {"code": "animation", "short_name": "a", "id": -2},
]
SHOTGRID_DATA_ASSETS = [
    {
        "type": "Asset",
        "code": "Fork1",
        FIELD_ASSET_TYPE: "MXB",
        FIELD_ASSET_ID: 11001,
        "tasks": [
            {
                FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
                "name": "look",
                "type": "Task",
                FIELD_TASK_STEP: {"name": "modeling"},
                "sg_status_list": str(uuid.uuid4()),
                FIELD_TASK_ENTITY: {
                    "type": "Asset",
                    "name": "Fork1",
                    "id": 11001,
                },
            },
            {
                FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
                "name": "dev",
                "type": "Task",
                FIELD_TASK_STEP: {"name": "rigging"},
                "sg_status_list": str(uuid.uuid4()),
                FIELD_TASK_ENTITY: {
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
        FIELD_SHOT_ID: 110,
        FIELD_SHOT_SEQUENCE: {"id": 1, "name": "SQ_1", "type": "Sequence"},
        FIELD_SHOT_EPISODE: {"id": 1, "name": "EP_1", "type": "Episode"},
        "code": "SHOT10",
        FIELD_SHOT_SEQUENCE_EP: {
            "id": 1,
            "name": "EP_1",
            "type": "Episode",
        },
    },
    {
        "type": "Shot",
        FIELD_SHOT_ID: 111,
        FIELD_SHOT_SEQUENCE: {"id": 1, "name": "SQ_1", "type": "Sequence"},
        FIELD_SHOT_EPISODE: {"id": 1, "name": "EP_1", "type": "Episode"},
        "code": "SHOT11",
        FIELD_SHOT_SEQUENCE_EP: {
            "id": 1,
            "name": "EP_1",
            "type": "Episode",
        },
    },
    {
        "type": "Shot",
        FIELD_SHOT_ID: 112,
        FIELD_SHOT_SEQUENCE: {"id": 11, "name": "SQ_11", "type": "Sequence"},
        FIELD_SHOT_EPISODE: {"id": 1, "name": "EP_1", "type": "Episode"},
        "code": "SHOT12",
        FIELD_SHOT_SEQUENCE_EP: {
            "id": 1,
            "name": "EP_1",
            "type": "Episode",
        },
    },
    {
        "type": "Shot",
        FIELD_SHOT_ID: 113,
        FIELD_SHOT_SEQUENCE: {"id": 11, "name": "SQ_11", "type": "Sequence"},
        FIELD_SHOT_EPISODE: {"id": 1, "name": "EP_1", "type": "Episode"},
        "code": "SHOT13",
        FIELD_SHOT_SEQUENCE_EP: {
            "id": 1,
            "name": "EP_1",
            "type": "Episode",
        },
    },
    {
        "type": "Shot",
        FIELD_SHOT_ID: 120,
        FIELD_SHOT_SEQUENCE: {"id": 2, "name": "SQ_2", "type": "Sequence"},
        FIELD_SHOT_EPISODE: {"id": 2, "name": "EP_2", "type": "Episode"},
        "code": "SHOT20",
        FIELD_SHOT_SEQUENCE_EP: {
            "id": 2,
            "name": "EP_2",
            "type": "Episode",
        },
    },
    {
        "type": "Shot",
        FIELD_SHOT_ID: 121,
        FIELD_SHOT_SEQUENCE: {"id": 2, "name": "SQ_2", "type": "Sequence"},
        FIELD_SHOT_EPISODE: {"id": 2, "name": "EP_2", "type": "Episode"},
        "code": "SHOT21",
        FIELD_SHOT_SEQUENCE_EP: {
            "id": 2,
            "name": "EP_2",
            "type": "Episode",
        },
    },
]
SHOTGRID_DATA_TASKS = [
    {
        FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
        "content": "color",
        FIELD_TASK_STEP: {"name": "render"},
        "sg_status_list": str(uuid.uuid4()),
        FIELD_TASK_ENTITY: {
            "type": "Shot",
            "name": "SHOT10",
            "id": 110,
        },
    },
    {
        FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
        "content": "dev",
        FIELD_TASK_STEP: {"name": "layout"},
        "sg_status_list": str(uuid.uuid4()),
        FIELD_TASK_ENTITY: {
            "type": "Shot",
            "name": "SHOT10",
            "id": 110,
        },
    },
    {
        FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
        "content": "color",
        FIELD_TASK_STEP: {"name": "layout"},
        "sg_status_list": str(uuid.uuid4()),
        FIELD_TASK_ENTITY: {
            "type": "Shot",
            "name": "SHOT11",
            "id": 111,
        },
    },
    {
        FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
        "content": "look",
        FIELD_TASK_STEP: {"name": "layout"},
        "sg_status_list": str(uuid.uuid4()),
        FIELD_TASK_ENTITY: {
            "type": "Shot",
            "name": "SHOT11",
            "id": 111,
        },
    },
    {
        FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
        "content": "lines",
        "sg_status_list": str(uuid.uuid4()),
        FIELD_TASK_STEP: {"name": "layout"},
        FIELD_TASK_ENTITY: {
            "type": "Shot",
            "name": "SHOT10",
            "id": 110,
        },
    },
    {
        FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
        "content": "look",
        "sg_status_list": str(uuid.uuid4()),
        FIELD_TASK_STEP: {"name": "render"},
        FIELD_TASK_ENTITY: {
            "type": "Shot",
            "name": "SHOT10",
            "id": 110,
        },
    },
    {
        FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
        "content": "look",
        "sg_status_list": str(uuid.uuid4()),
        FIELD_TASK_STEP: {"name": "layout"},
        FIELD_TASK_ENTITY: {
            "type": "Shot",
            "name": "SHOT11",
            "id": 111,
        },
    },
    {
        FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
        "content": "look",
        "sg_status_list": str(uuid.uuid4()),
        FIELD_TASK_STEP: {"name": "animation"},
        FIELD_TASK_ENTITY: {
            "type": "Shot",
            "name": "SHOT11",
            "id": 111,
        },
    },
    {
        FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
        "content": "color",
        "sg_status_list": str(uuid.uuid4()),
        FIELD_TASK_STEP: {"name": "layout"},
        FIELD_TASK_ENTITY: {
            "type": "Shot",
            "name": "SHOT20",
            "id": 120,
        },
    },
    {
        FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
        "content": "dev",
        "sg_status_list": str(uuid.uuid4()),
        FIELD_TASK_STEP: {"name": "animation"},
        FIELD_TASK_ENTITY: {
            "type": "Shot",
            "name": "SHOT20",
            "id": 120,
        },
    },
    {
        FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
        "content": "dev",
        "sg_status_list": str(uuid.uuid4()),
        FIELD_TASK_STEP: {"name": "render"},
        FIELD_TASK_ENTITY: {
            "type": "Shot",
            "name": "SHOT21",
            "id": 121,
        },
    },
    {
        FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
        "content": "look",
        "sg_status_list": str(uuid.uuid4()),
        FIELD_TASK_STEP: {"name": "render"},
        FIELD_TASK_ENTITY: {
            "type": "Shot",
            "name": "SHOT21",
            "id": 121,
        },
    },
    {
        FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
        "content": "look",
        "sg_status_list": str(uuid.uuid4()),
        FIELD_TASK_STEP: {"name": "modeling"},
        FIELD_TASK_ENTITY: {"type": "Asset", "name": "Fork1", "id": 11001},
    },
    {
        FIELD_TASK_ID: _RAND(10 ** 2, 10 ** 10),
        "content": "dev",
        "sg_status_list": str(uuid.uuid4()),
        FIELD_TASK_STEP: {"name": "rigging"},
        FIELD_TASK_ENTITY: {"type": "Asset", "name": "Fork1", "id": 11001},
    },
]
SHOTGRID_ASSET_TO_ASSET_LINKS = []
SHOTGRID_SHOT_TO_SHOT_LINKS = []
SHOTGRID_ASSET_TO_SHOT_LINKS = []
