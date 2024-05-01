from enum import Enum
from typing import Any, Callable

__all__ = ["NV_T"]

# リンター対策の定義
_: Callable


class NV_T(Enum):
    OK = "Ok"
    RETURN = "return"

    WELCOME_MESSAGE = "Hello World!\nWelcome to MisT with MVVM model!"
    QUIT = "Quit?"
    NOTE_NONE = "Please get note."

    def __getattribute__(self, __name: str) -> Any:
        if __name == "value":
            return _(super().__getattribute__(__name))
        return super().__getattribute__(__name)
