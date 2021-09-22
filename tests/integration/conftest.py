from itertools import chain
from typing import Any

from assertpy import add_extension


def except_by_key(self: Any, key: str) -> Any:
    if type(self.val) != list:
        self.error(f"{self.val} must be of type list!")
    self.val = [{k: v for (k, v) in x.items() if k != key} for x in self.val]
    return self


def extract_keys(self: Any) -> Any:
    if type(self.val) != list:
        self.error(f"{self.val} must be of type list!")
    self.val = set(chain(*[[k for (k, v) in x.items()] for x in self.val]))
    return self


add_extension(extract_keys)
add_extension(except_by_key)
