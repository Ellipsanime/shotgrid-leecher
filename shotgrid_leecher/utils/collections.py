from itertools import chain, starmap
from typing import Dict, Any, Tuple, Iterable, Set

from toolz import curry

Map = Dict[str, Any]


@curry
def drop_keys(keys: Set[str], dic: Map) -> Map:
    return {k: v for k, v in dic.items() if k not in keys}


@curry
def keep_keys(keys: Set[str], dic: Map) -> Map:
    return {k: v for k, v in dic.items() if k in keys}


def _unpack_nested(
    key: str, value: Any, sep: str = "."
) -> Iterable[Tuple[str, Any]]:
    value_type = type(value)
    if value_type is dict:
        if not value:
            yield key, None
        for k, v in value.items():
            yield f"{key}{sep}{k}", v
    if value_type is not dict:
        yield key, value


def flatten_dict(dictionary: Map) -> Map:
    dict_ = dictionary
    while True:
        dict_ = dict(
            chain.from_iterable(starmap(_unpack_nested, dict_.items()))
        )
        if not any(type(x) is dict for x in dict_.values()):
            return dict_


def swap_mapping_keys_values(mapping: Dict[str, str], target: Map) -> Map:
    return {k: target[v] for k, v in mapping.items() if v in target}
