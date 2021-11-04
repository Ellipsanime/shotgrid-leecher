from enum import Enum
from typing import Any

import attr
from mypy.messages import capitalize


def format_path(path: str) -> str:
    return f",{','.join([x for x in path.split('/') if x])},"


def snakify_camel(target: str) -> str:
    raw = "".join(
        [f"_{c.lower()}" if c.isupper() else c for c in target]
    ).lstrip("_")
    return "_".join([x for x in raw.split("_") if x])


def avalonify_snake_case(target: str) -> str:
    exceptions = {"tools_env"}
    if target in exceptions:
        return target
    raw = [x for x in target.strip("_").split("_") if x]
    return "".join(
        [x if not l else capitalize(x) for x, l in zip(raw, range(len(raw)))]
    )


def attr_value_to_dict(*args) -> Any:
    _, _, val = args
    if attr.has(val) and hasattr(val, "to_dict"):
        return val.to_dict()
    if attr.has(val):
        return attr.asdict(val)
    if isinstance(val, Enum):
        return val.value
    return val
