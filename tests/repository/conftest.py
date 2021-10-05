from typing import List, Any, Optional, Dict

from assertpy import add_extension
from toolz import pipe
from toolz.curried import (
    filter as where,
    map as select,
)


def _find_by_type(target: List[Dict], raw_path: str, type_: str) -> List[str]:
    def exact(x):
        return x["parent"] == raw_path

    def wild(x):
        return (x.get("parent") or "").startswith(raw_path[:-1])

    filter_fn = wild if raw_path.endswith("*") else exact
    return pipe(
        target,
        where(filter_fn),
        where(lambda x: x["type"] == type_),
        select(lambda x: x["type"]),
        list,
    )


def path_has_types(self: Any, path: Optional[str], content: List[str]):
    if type(self.val) != list:
        self.error(f"{self.val} must be of type list!")

    actual_content = pipe(
        self.val,
        where(lambda x: x["parent"] == path),
        select(lambda x: x["type"]),
        set,
    )
    if len(set(content).difference(actual_content)) > 0:
        return self.error(
            f"Actual {list(actual_content)} is not equal to expected {content}"
        )
    return self


def path_counts_tasks(self: Any, path: Optional[str], count: int = 0) -> Any:
    if type(self.val) != list:
        self.error(f"{self.val} must be of type list!")
    actual_task = _find_by_type(self.val, path, "Task")
    if len(actual_task) != count:
        return self.error(
            f"Expected task count {count} is not "
            f"equal to actual {len(actual_task)} in {actual_task}"
        )
    return self


def path_counts_types(
    self: Any,
    path: Optional[str],
    shot=0,
    episode=0,
    group=0,
    sequence=0,
    task=0,
    asset=0,
) -> Any:
    if type(self.val) != list:
        self.error(f"{self.val} must be of type list!")

    actual_asset = _find_by_type(self.val, path, "Asset")
    actual_shot = _find_by_type(self.val, path, "Shot")
    actual_episode = _find_by_type(self.val, path, "Episode")
    actual_group = _find_by_type(self.val, path, "Group")
    actual_sequence = _find_by_type(self.val, path, "Sequence")

    if len(actual_asset) != asset:
        return self.error(
            f"Expected shot count {shot} is not "
            f"equal to actual {len(actual_asset)} in {actual_asset}"
        )
    if len(actual_shot) != shot:
        return self.error(
            f"Expected shot count {shot} is not "
            f"equal to actual {len(actual_shot)} in {actual_shot}"
        )
    if len(actual_episode) != episode:
        return self.error(
            f"Expected episode count {episode} is not "
            f"equal to actual {len(actual_episode)} in {actual_episode}"
        )
    if len(actual_group) != group:
        return self.error(
            f"Expected group count {group} is not "
            f"equal to actual {len(actual_group)} in {actual_group}"
        )
    if len(actual_sequence) != sequence:
        return self.error(
            f"Expected sequence count {sequence} is not "
            f"equal to actual {len(actual_sequence)} in {actual_sequence}"
        )
    return path_counts_tasks(self, path, task)


add_extension(path_has_types)
add_extension(path_counts_types)
add_extension(path_counts_tasks)
