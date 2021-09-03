from typing import List, Any, Optional

from assertpy import add_extension
from toolz import pipe
from toolz.curried import (
    filter as where,
    map as select,
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


add_extension(path_has_types)

