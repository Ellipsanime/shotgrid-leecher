from typing import Callable, Any, Optional

Anything = Exception


def try_or(fun: Callable, or_: Optional[Any] = None, *args) -> Any:
    try:
        return fun(*args)
    except Anything:
        return or_


def try_or_call(fun: Callable, or_call: Callable, *args) -> Any:
    try:
        return fun(*args)
    except Anything:
        return or_call(*args)
