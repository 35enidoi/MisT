from enum import Enum
from typing import Any, Callable

__all__ = ["NV_T"]

# リンター対策の定義
_: Callable


class NV_T(Enum):
    OK = "Ok"
    RETURN = "return"

    QUIT_BUTTON = "Quit"
    GET_NOTE_BUTTON = "Get note"
    CONFIG_BUTTON = "Config"

    GET_NOTE_SUCCESS = "Succeed in getting note!"
    GET_NOTE_FAIL = "Something occured while get note."
    GET_NOTE_FAIL_ADDITIONAL_1 = "Probably because there is no token."
    GET_NOTE_FAIL_ADDITIONAL_2 = "Probably because select invalid TL"

    GET_NOTE_MISSKEYPY_INVALID = "misskeypy is invalid. reconnect instance please"

    WELCOME_MESSAGE = "Hello World!\nWelcome to MisT with MVVM model!"
    QUIT = "Quit?"
    NOTE_NONE = "Please get note."

    def __getattribute__(self, __name: str) -> Any:
        if __name == "value":
            return _(super().__getattribute__(__name))
        return super().__getattribute__(__name)
