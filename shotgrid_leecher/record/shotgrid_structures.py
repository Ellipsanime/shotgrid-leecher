from dataclasses import dataclass
from enum import unique, Enum
from typing import Optional, List


@unique
class ShotgridRefType(Enum):
    UNKNOWN = "Unknown"
    CUSTOM_TYPE = "custom_type"
    ASSET = "Asset"
    PROJECT = "Project"
    LIST = "List"
    EMPTY = "Empty"
    SEQUENCE = "Sequence"
    SHOT = "Shot"
    SCENE = "Scene"
    EPISODE = "Episode"
    TASK = "Task"


@dataclass(frozen=True)
class ShotgridRef:
    type: ShotgridRefType
    id: Optional[int]


@dataclass(frozen=True)
class ExtraNodeParams:
    fps: float
    frame_start: int
    frame_end: int
    handle_start: int
    handle_end: int
    width: int
    height: int
    cap_in: int
    cap_out: int
    pixel_aspect: float
    tools: Optional[str] = None


@dataclass(frozen=True)
class ShotgridNode:
    label: str
    path: str
    ref: ShotgridRef
    children: List["ShotgridNode"]
    extra_params: Optional[ExtraNodeParams] = None

    def copy_with(
        self,
        children: List["ShotgridNode"],
        extra_params: Optional[ExtraNodeParams] = None,
    ) -> "ShotgridNode":
        return ShotgridNode(
            self.label,
            self.path,
            self.ref,
            children,
            extra_params,
        )
