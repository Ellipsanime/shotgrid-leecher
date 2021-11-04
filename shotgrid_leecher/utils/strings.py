from enum import Enum
from typing import Any

import attr


def format_path(path: str) -> str:
    return f",{','.join([x for x in path.split('/') if x])},"


def snakify_camel(target: str) -> str:
    raw = "".join(
        [f"_{c.lower()}" if c.isupper() else c for c in target]
    ).lstrip("_")
    return "_".join([x for x in raw.split("_") if x])


def attr_value_to_dict(*args) -> Any:
    _, _, val = args
    if attr.has(val) and hasattr(val, "to_dict"):
        return val.to_dict()
    if attr.has(val):
        return attr.asdict(val)
    if isinstance(val, Enum):
        return val.value
    return val
