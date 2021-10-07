from typing import List, Any, Dict

import attr


class BaseFilter:
    def to_sublist(self) -> List[Any]:
        raise RuntimeError("Not yet implemented")

    def to_list(self) -> List[List[Any]]:
        return [self.to_sublist()]


@attr.s(auto_attribs=True, frozen=True)
class IsFilter(BaseFilter):
    type: str
    value: Dict[str, Any]

    def to_sublist(self) -> List[Any]:
        return [self.type, "is", self.value]


@attr.s(auto_attribs=True, frozen=True)
class IsNotFilter(BaseFilter):
    key: str
    value: Any

    def to_sublist(self) -> List[Any]:
        return [self.key, "is_not", self.value]


@attr.s(auto_attribs=True, frozen=True)
class IdFilter(BaseFilter):
    id: int

    def to_sublist(self) -> List[Any]:
        return ["id", "is", self.id]


@attr.s(auto_attribs=True, frozen=True)
class CompositeFilter(BaseFilter):
    filters: List[BaseFilter]

    def to_list(self) -> List[List[Any]]:
        return [x.to_sublist() for x in self.filters]

    @staticmethod
    def filter_by(*filters: BaseFilter) -> List[List[Any]]:
        return CompositeFilter(list(filters)).to_list()
