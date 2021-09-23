from itertools import chain, starmap
from typing import Dict, Any, Tuple, Iterable


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


def flatten_dict(dictionary: Dict[str, Any]) -> Dict[str, Any]:
    dict_ = dictionary
    while True:
        dict_ = dict(
            chain.from_iterable(starmap(_unpack_nested, dict_.items()))
        )
        if not any(type(x) is dict for x in dict_.values()):
            return dict_