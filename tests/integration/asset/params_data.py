import random
import uuid

from toolz import compose

from shotgrid_leecher.record.enums import ShotgridField

_RAND = random.randint

_D = compose(
    lambda x: None if x % 5 == 0 else x,
    float,
    lambda: uuid.uuid4().int,
)

PROJECT_ID = f"Project_{str(uuid.uuid4())[:5]}"

SHOTGRID_DATA_PROJECT = [
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "name": PROJECT_ID,
        "type": "Project",
    }
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
                "content": "look",
                "step": {"name": "modeling"},
                ShotgridField.ENTITY.value: {
                    "type": "Asset",
                    "name": "Fork1",
                    "id": 11001,
                },
            },
            {
                "id": _RAND(10 ** 2, 10 ** 10),
                "content": "dev",
                "step": {"name": "rigging"},
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
        **(
            {
                ShotgridField.CUT_IN.value: _D(),
                ShotgridField.CUT_OUT.value: _D(),
                ShotgridField.HEAD_IN.value: _D(),
                ShotgridField.TAIL_OUT.value: _D(),
            }
            if _RAND(10 ** 2, 10 ** 10) % 2 == 0
            else {}
        ),
    },
    {
        "type": "Shot",
        "id": 111,
        "sequence": {"id": 1, "name": "SQ_1", "type": "Sequence"},
        "episode": {"id": 1, "name": "EP_1", "type": "Episode"},
        "code": "SHOT11",
        ShotgridField.SEQUENCE_EPISODE.value: {
            "id": 1,
            "name": "EP_1",
            "type": "Episode",
        },
        **(
            {
                ShotgridField.CUT_IN.value: _D(),
                ShotgridField.CUT_OUT.value: _D(),
                ShotgridField.HEAD_IN.value: _D(),
                ShotgridField.TAIL_OUT.value: _D(),
            }
            if _RAND(10 ** 2, 10 ** 10) % 2 == 0
            else {}
        ),
    },
    {
        "type": "Shot",
        "id": 112,
        "sequence": {"id": 11, "name": "SQ_11", "type": "Sequence"},
        "episode": {"id": 1, "name": "EP_1", "type": "Episode"},
        "code": "SHOT12",
        ShotgridField.SEQUENCE_EPISODE.value: {
            "id": 1,
            "name": "EP_1",
            "type": "Episode",
        },
        **(
            {
                ShotgridField.CUT_IN.value: _D(),
                ShotgridField.CUT_OUT.value: _D(),
                ShotgridField.HEAD_IN.value: _D(),
                ShotgridField.TAIL_OUT.value: _D(),
            }
            if _RAND(10 ** 2, 10 ** 10) % 2 == 0
            else {}
        ),
    },
    {
        "type": "Shot",
        "id": 113,
        "sequence": {"id": 11, "name": "SQ_11", "type": "Sequence"},
        "episode": {"id": 1, "name": "EP_1", "type": "Episode"},
        "code": "SHOT13",
        ShotgridField.SEQUENCE_EPISODE.value: {
            "id": 1,
            "name": "EP_1",
            "type": "Episode",
        },
        **(
            {
                ShotgridField.CUT_IN.value: _D(),
                ShotgridField.CUT_OUT.value: _D(),
                ShotgridField.HEAD_IN.value: _D(),
                ShotgridField.TAIL_OUT.value: _D(),
            }
            if _RAND(10 ** 2, 10 ** 10) % 2 == 0
            else {}
        ),
    },
    {
        "type": "Shot",
        "id": 120,
        "sequence": {"id": 2, "name": "SQ_2", "type": "Sequence"},
        "episode": {"id": 2, "name": "EP_2", "type": "Episode"},
        "code": "SHOT20",
        ShotgridField.SEQUENCE_EPISODE.value: {
            "id": 2,
            "name": "EP_2",
            "type": "Episode",
        },
        **(
            {
                ShotgridField.CUT_IN.value: _D(),
                ShotgridField.CUT_OUT.value: _D(),
                ShotgridField.HEAD_IN.value: _D(),
                ShotgridField.TAIL_OUT.value: _D(),
            }
            if _RAND(10 ** 2, 10 ** 10) % 2 == 0
            else {}
        ),
    },
    {
        "type": "Shot",
        "id": 121,
        "sequence": {"id": 2, "name": "SQ_2", "type": "Sequence"},
        "episode": {"id": 2, "name": "EP_2", "type": "Episode"},
        "code": "SHOT21",
        ShotgridField.SEQUENCE_EPISODE.value: {
            "id": 2,
            "name": "EP_2",
            "type": "Episode",
        },
        **(
            {
                ShotgridField.CUT_IN.value: _D(),
                ShotgridField.CUT_OUT.value: _D(),
                ShotgridField.HEAD_IN.value: _D(),
                ShotgridField.TAIL_OUT.value: _D(),
            }
            if _RAND(10 ** 2, 10 ** 10) % 2 == 0
            else {}
        ),
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
        "content": "color",
        "step": {"name": "layout"},
        ShotgridField.ENTITY.value: {
            "type": "Shot",
            "name": "SHOT11",
            "id": 111,
        },
    },
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "look",
        "step": {"name": "layout"},
        ShotgridField.ENTITY.value: {
            "type": "Shot",
            "name": "SHOT11",
            "id": 111,
        },
    },
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "lines",
        "step": {"name": "layout"},
        ShotgridField.ENTITY.value: {
            "type": "Shot",
            "name": "SHOT10",
            "id": 110,
        },
    },
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "look",
        "step": {"name": "render"},
        ShotgridField.ENTITY.value: {
            "type": "Shot",
            "name": "SHOT10",
            "id": 110,
        },
    },
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "look",
        "step": {"name": "layout"},
        ShotgridField.ENTITY.value: {
            "type": "Shot",
            "name": "SHOT11",
            "id": 111,
        },
    },
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "look",
        "step": {"name": "animation"},
        ShotgridField.ENTITY.value: {
            "type": "Shot",
            "name": "SHOT11",
            "id": 111,
        },
    },
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "color",
        "step": {"name": "layout"},
        ShotgridField.ENTITY.value: {
            "type": "Shot",
            "name": "SHOT20",
            "id": 120,
        },
    },
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "dev",
        "step": {"name": "animation"},
        ShotgridField.ENTITY.value: {
            "type": "Shot",
            "name": "SHOT20",
            "id": 120,
        },
    },
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "dev",
        "step": {"name": "render"},
        ShotgridField.ENTITY.value: {
            "type": "Shot",
            "name": "SHOT21",
            "id": 121,
        },
    },
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "look",
        "step": {"name": "render"},
        ShotgridField.ENTITY.value: {
            "type": "Shot",
            "name": "SHOT21",
            "id": 121,
        },
    },
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "look",
        "step": {"name": "modeling"},
        ShotgridField.ENTITY.value: {
            "type": "Asset",
            "name": "Fork1",
            "id": 11001,
        },
    },
    {
        "id": _RAND(10 ** 2, 10 ** 10),
        "content": "dev",
        "step": {"name": "rigging"},
        ShotgridField.ENTITY.value: {
            "type": "Asset",
            "name": "Fork1",
            "id": 11001,
        },
    },
]
