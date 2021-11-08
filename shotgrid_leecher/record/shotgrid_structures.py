from enum import unique, Enum
from typing import Optional, List, Dict, Any, Iterator

import attr

from shotgrid_leecher.utils.strings import format_path


@attr.s(auto_attribs=True, frozen=True)
class ShotgridEntity:
    id: int


@attr.s(auto_attribs=True, frozen=True)
class ShotgridNamedEntity(ShotgridEntity):
    name: str
    type: str


@attr.s(auto_attribs=True, frozen=True)
class ShotgridTaskStep(ShotgridEntity):
    name: str


@attr.s(auto_attribs=True, frozen=True)
class ShotgridTaskEntity(ShotgridNamedEntity):
    pass


@attr.s(auto_attribs=True, frozen=True)
class ShotgridShotEpisode(ShotgridNamedEntity):
    pass


@attr.s(auto_attribs=True, frozen=True)
class ShotgridShotSequence(ShotgridNamedEntity):
    pass


@attr.s(auto_attribs=True, frozen=True)
class ShotgridAssetTask(ShotgridNamedEntity):
    pass


@attr.s(auto_attribs=True, frozen=True)
class ShotgridShotParams:
    cut_in: Optional[int]
    cut_out: Optional[int]
    head_in: Optional[int]
    head_out: Optional[int]
    tail_in: Optional[int]
    tail_out: Optional[int]
    cut_duration: Optional[int]
    frame_rate: Optional[int]

    def to_dict(self) -> Dict[str, Any]:
        return attr.asdict(self)


@attr.s(auto_attribs=True, frozen=True)
class ShotgridShot(ShotgridEntity):
    code: str
    type: str
    id: int
    params: Optional[ShotgridShotParams]
    sequence: Optional[ShotgridShotSequence]
    episode: Optional[ShotgridShotEpisode]
    sequence_episode: Optional[ShotgridShotEpisode]

    def has_params(self) -> bool:
        return self.params is not None and bool(
            tuple(filter(lambda x: x, attr.astuple(self)))
        )

    def episode_id(self) -> Optional[int]:
        return self.episode.id if self.episode else None

    def episode_name(self) -> Optional[str]:
        return self.episode.name if self.episode else None

    def sequence_name(self) -> Optional[str]:
        return self.sequence.name if self.sequence else None

    def copy_with(self, **changes) -> "ShotgridShot":
        return attr.evolve(self, **changes)

    def copy_with_sequence(self, seq: ShotgridShotSequence) -> "ShotgridShot":
        return attr.evolve(self, **{"sequence": seq})

    def copy_with_episode(self, ep: ShotgridShotEpisode) -> "ShotgridShot":
        return attr.evolve(self, **{"episode": ep})

    def copy_with_sequence_episode(
        self,
        ep: ShotgridShotEpisode,
    ) -> "ShotgridShot":
        return attr.evolve(self, **{"sequence_episode": ep})


@attr.s(auto_attribs=True, frozen=True)
class ShotgridTask(ShotgridEntity):
    content: str
    entity: ShotgridTaskEntity
    step: Optional[ShotgridTaskStep]

    def step_name(self) -> Optional[str]:
        return self.step.name if self.step else None

    def copy_with_step(self, step: ShotgridTaskStep) -> "ShotgridTask":
        return attr.evolve(self, **{"step": step})


@attr.s(auto_attribs=True, frozen=True)
class ShotgridAsset(ShotgridEntity):
    id: int
    type: str
    code: str
    asset_type: str
    tasks: List[ShotgridTask]

    def copy_with_tasks(self, tasks: List[ShotgridTask]) -> "ShotgridAsset":
        return attr.evolve(self, **{"tasks": tasks})


@attr.s(auto_attribs=True, frozen=True)
class ShotgridCredentials:
    shotgrid_url: str
    script_name: str
    script_key: str

    @staticmethod
    def from_struct(struct: Any) -> "ShotgridCredentials":
        if not attr.has(type(struct)):
            raise Exception(f"Unsupported type {type(struct)} of {struct}")
        return ShotgridCredentials.from_dict(attr.asdict(struct))

    @staticmethod
    def from_dict(dic: Dict[str, Any]) -> "ShotgridCredentials":
        return ShotgridCredentials(
            shotgrid_url=dic["shotgrid_url"],
            script_name=dic["script_name"],
            script_key=dic["script_key"],
        )


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


@attr.s(auto_attribs=True, frozen=True)
class ShotgridRef:
    type: ShotgridRefType
    id: Optional[int]

    def to_row(self) -> Dict[str, Any]:
        return {
            "ref_type": self.type.value,
            "ref_id": self.id,
        }


@attr.s(auto_attribs=True, frozen=True)
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


@attr.s(auto_attribs=True, frozen=True)
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


@attr.s(auto_attribs=True, frozen=True)
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
        return attr.evolve(self, children=children)

    def copy_with_parent_paths(
        self, parent_paths: ShotgridParentPaths
    ) -> "ShotgridNode":
        return attr.evolve(self, parent_paths=parent_paths)
