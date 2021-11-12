from itertools import chain, starmap
from typing import Dict, Any, Tuple, Iterable, Set

from toolz import curry

Map = Dict[str, Any]
_DEF_SEP = "."


@curry
def drop_keys(keys: Set[str], dic: Map) -> Map:
    return {k: v for k, v in dic.items() if k not in keys}


@curry
def keep_keys(keys: Set[str], dic: Map) -> Map:
    return {k: v for k, v in dic.items() if k in keys}


@curry
def _unpack_nested(
    except_: Set[str],
    key: str,
    value: Any,
    sep: str = _DEF_SEP,
) -> Iterable[Tuple[str, Any]]:
    value_type = type(value)
    if value_type is dict and key not in except_:
        if not value:
            yield key, None
        for k, v in value.items():
            yield f"{key}{sep}{k}", v
    if value_type is not dict:
        yield key, value
    if key in except_:
        yield key, value


def flatten_dict(dictionary: Map, except_: Set[str] = set()) -> Map:
    dict_ = dictionary
    while True:
        dict_ = dict(
            chain.from_iterable(
                starmap(_unpack_nested(except_), dict_.items())
            )
        )
        if not any(
            type(v) is dict for k, v in dict_.items() if k not in except_
        ):
            return dict_


def swap_mapping_keys_values(mapping: Dict[str, str], target: Map) -> Map:
    return {k: target[v] for k, v in mapping.items() if v in target}
