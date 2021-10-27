from typing import Callable, Any

Anything = Exception


def try_or(fun: Callable, or_: Any, *args) -> Any:
    try:
        return fun(*args)
    except Anything:
        return or_
