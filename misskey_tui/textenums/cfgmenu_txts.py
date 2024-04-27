from enum import Enum
from typing import Any, Callable

__all__ = ["CM_T"]

# リンター対策の定義
_: Callable


class CM_T(Enum):
    RETURN = "return"
    OK = "Ok"
    SUCCESS = "success"

    def __getattribute__(self, __name: str) -> Any:
        if __name == "value":
            return _(super().__getattribute__(__name))
        return super().__getattribute__(__name)