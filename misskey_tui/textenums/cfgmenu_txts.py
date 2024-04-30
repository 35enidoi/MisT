from enum import Enum
from typing import Any, Callable

__all__ = ["CM_T"]

# リンター対策の定義
_: Callable


class CM_T(Enum):
    RETURN = "return"
    OK = "Ok"
    SUCCESS = "success"

    TOKEN_BUTTON = "Token"
    TOKEN_QUESTION = "hatena"
    TOKEN_SEL_0 = "Set Token"
    TOKEN_SET_WRITE_PLS = "Write TOKEN please"

    CLEAR_BUTTON = "Clear"

    def __getattribute__(self, __name: str) -> Any:
        if __name == "value":
            return _(super().__getattribute__(__name))
        return super().__getattribute__(__name)
