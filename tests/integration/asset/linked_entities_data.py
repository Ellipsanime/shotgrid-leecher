import random
import uuid

from bson import ObjectId
from toolz import compose

from shotgrid_leecher.record.avalon_structures import AvalonProjectData
from shotgrid_leecher.record.enums import ShotgridField
from shotgrid_leecher.record.intermediate_structures import IntermediateParams
from shotgrid_leecher.utils.collections import drop_keys
from shotgrid_leecher.utils.ids import to_object_id

_RAND = random.randint

_I32 = compose(
    lambda x: x * 2 if x % 5 == 0 else x,
    lambda: _RAND(10 ** 2, 10 ** 10),
)

_PROJ_DATA = IntermediateParams(
    **drop_keys(
        {"library_project"},
        AvalonProjectData().to_dict(),
    )
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
SHOTGRID_DATA_STEPS = [
    {"code": "modeling", "short_name": "m", "id": -4},
    {"code": "rigging", "short_name": "r", "id": -4},
    {"code": "render", "short_name": "re", "id": -4},
    {"code": "layout", "short_name": "l", "id": -4},
    {"code": "animation", "short_name": "a", "id": -4},
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
        "assets": [
            {"id": -1, "name": "nope1", "type": "Asset"},
            {"id": -2, "name": "nope2", "type": "Asset"},
            {"id": 11001, "name": "Fork1", "type": "Asset"},
        ],
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
INTERMEDIATE_DB_DATA = [
    {
        "type": "Project",
        "src_id": 9545477334,
        "code": f"{PROJECT_ID}",
        "config": {},
        "params": _PROJ_DATA.to_dict(),
        "object_id": ObjectId("6193de6d421ac9b68965514f"),
        "parent": None,
        "_id": "Project_a166d",
    },
    {
        "parent": f",{PROJECT_ID},",
        "src_id": None,
        "params": _PROJ_DATA.to_dict(),
        "code": None,
        "type": "Group",
        "object_id": ObjectId("6193de6d421ac9b689655150"),
        "_id": "Asset",
    },
    {
        "parent": f",{PROJECT_ID},Asset,",
        "src_id": None,
        "code": None,
        "params": _PROJ_DATA.to_dict(),
        "type": "Group",
        "object_id": ObjectId("6193de6d421ac9b689655151"),
        "_id": "MXB",
    },
    {
        "parent": f",{PROJECT_ID},Asset,MXB,",
        "code": None,
        "type": "Asset",
        "src_id": 11001,
        "params": _PROJ_DATA.to_dict(),
        "object_id": to_object_id(11001),
        "_id": "Fork1",
    },
    {
        "parent": f",{PROJECT_ID},",
        "src_id": None,
        "code": None,
        "params": _PROJ_DATA.to_dict(),
        "type": "Group",
        "object_id": ObjectId("6193de6d421ac9b689655153"),
        "_id": "Shot",
    },
    {
        "parent": f",{PROJECT_ID},Shot,",
        "code": None,
        "type": "Shot",
        "params": _PROJ_DATA.to_dict(),
        "src_id": 110,
        "linked_entities": [
            {
                "id": 11001,
                "name": "Fork1",
                "object_id": to_object_id(11001),
            },
            {
                "id": 11002,
                "name": "Fork2",
                "object_id": ObjectId("6193de6d421ac9b689655153"),
            },
        ],
        "object_id": ObjectId("6193de6d421ac9b689655154"),
        "_id": "SHOT10",
    },
]
SHOTGRID_ASSET_TO_ASSET_LINKS = [
    {
        "type": "AssetAssetConnection",
        "id": 911010,
        "parent.Asset.id": 11001000,
        "asset.Asset.id": 11001,
        "cached_display_name": "Asset 11001000 Asset 11001",
        "sg_instance": 15,
    },
    {
        "type": "AssetAssetConnection",
        "id": 911010,
        "parent.Asset.id": -11001000,
        "asset.Asset.id": 11001,
        "cached_display_name": "Asset -11001000 Asset 11001",
    },
]
SHOTGRID_SHOT_TO_SHOT_LINKS = [
    {
        "type": "ShotShotConnection",
        "id": 911004,
        "shot.Shot.id": -1,
        "parent_shot.Shot.id": -1,
        "cached_display_name": "Asset -1 Shot -1",
        "sg_instance": 2,
    },
    {
        "type": "ShotShotConnection",
        "id": 911005,
        "shot.Shot.id": 110,
        "parent_shot.Shot.id": 99999,
        "cached_display_name": "Shot 99999 Shot 110",
        "sg_instance": 2,
    },
    {
        "type": "ShotShotConnection",
        "id": 911005,
        "shot.Shot.id": 110,
        "parent_shot.Shot.id": -99999,
        "cached_display_name": "Shot -99999 Shot 110",
    },
]
SHOTGRID_ASSET_TO_SHOT_LINKS = [
    {
        "type": "AssetShotConnection",
        "id": 911000,
        "shot.Shot.id": -1,
        "asset.Asset.id": -1,
        "cached_display_name": "Asset -1 Shot -1",
        "sg_locked_version": None,
        "sg_hard_locked": False,
    },
    {
        "type": "AssetShotConnection",
        "id": 911002,
        "shot.Shot.id": 110,
        "asset.Asset.id": 88_888,
        "cached_display_name": "Asset 88_888 Shot 110",
        "sg_instance": 5,
        "sg_locked_version": None,
        "sg_hard_locked": False,
    },
    {
        "type": "AssetShotConnection",
        "id": 911002,
        "shot.Shot.id": 110,
        "asset.Asset.id": -88_888,
        "cached_display_name": "Asset -88_888 Shot 110",
        "sg_locked_version": None,
        "sg_hard_locked": False,
    },
]
