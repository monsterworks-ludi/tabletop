from typing import Any

def unique(singleton: set) -> Any:
    if not len(singleton) == 1:
        raise RuntimeError("select_only making random selection")
    return next(iter(singleton))
