from dataclasses import dataclass
from enum import unique, Enum
from typing import Optional, List, Dict, Any, Iterator

from shotgrid_leecher.utils.strings import format_path


@dataclass(frozen=True)
class ShotgridEntity:
    id: int


@dataclass(frozen=True)
class ShotgridTaskStep(ShotgridEntity):
    name: str


@dataclass(frozen=True)
class ShotgridTaskEntity(ShotgridEntity):
    name: str


@dataclass(frozen=True)
class ShotgridTask(ShotgridEntity):
    content: str
    name: str
    entity: ShotgridTaskEntity
    step: Optional[ShotgridTaskStep]

    def copy_with_step(self, step: ShotgridTaskStep) -> "ShotgridTask":
        return ShotgridTask(
            **{
                **self.__dict__,
                "entity": self.entity,
                "step": step,
            }
        )


@dataclass(frozen=True)
class ShotgridCredentials:
    shotgrid_url: str
    script_name: str
    script_key: str


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

    def to_row(self) -> Dict[str, Any]:
        return {
            "ref_type": self.type.value,
            "ref_id": self.id,
        }


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

    @staticmethod
    def empty() -> Dict[str, Any]:
        return {
            "fps": None,
            "frame_start": None,
            "frame_end": None,
            "handle_start": None,
            "handle_end": None,
            "width": None,
            "height": None,
            "cap_in": None,
            "cap_out": None,
            "pixel_aspect": None,
            "tools": None,
        }


@dataclass(frozen=True)
class ShotgridParentPaths:
    system_path: str
    short_path: str

    @staticmethod
    def empty() -> Dict[str, Any]:
        return {
            "system_parent_path": None,
            "parent_path": None,
        }

    def to_row(self) -> Dict[str, Any]:
        return {
            "system_parent_path": format_path(self.system_path),
            "parent_path": format_path(self.short_path),
        }


@dataclass(frozen=True)
class ShotgridNode:
    label: str
    system_path: str
    ref: ShotgridRef
    children: List["ShotgridNode"]
    parent_paths: Optional[ShotgridParentPaths] = None
    extra_params: Optional[ExtraNodeParams] = None

    def to_table_iterator(self) -> Iterator[Dict[str, Any]]:
        parent_paths: Dict[str, Any] = (
            self.parent_paths.to_row()
            if self.parent_paths
            else ShotgridParentPaths.empty()
        )
        path = (
            f",{self.label},"
            if not parent_paths.get("short_path")
            else f"{parent_paths['short_path']}{self.label}"
        )
        yield {
            "_id": self.label,
            "path": path,
            "system_path": format_path(self.system_path or ""),
            **self.ref.to_row(),
            **parent_paths,
            **ExtraNodeParams.empty(),
        }
        for x in self.children:
            for y in x.to_table_iterator():
                yield y

    def copy_with_children(
        self, children: List["ShotgridNode"]
    ) -> "ShotgridNode":
        return ShotgridNode(
            self.label,
            self.system_path,
            self.ref,
            children,
            self.parent_paths,
            self.extra_params,
        )

    def copy_with_parent_paths(
        self, parent_paths: ShotgridParentPaths
    ) -> "ShotgridNode":
        return ShotgridNode(
            self.label,
            self.system_path,
            self.ref,
            self.children,
            parent_paths,
            self.extra_params,
        )
