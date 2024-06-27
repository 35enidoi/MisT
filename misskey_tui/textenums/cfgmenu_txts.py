from enum import Enum
from typing import Any, Callable

__all__ = ["CM_T"]

# リンター対策の定義
_: Callable[[str], str]


class CM_T(Enum):
    RETURN = "return"
    OK = "Ok"
    SUCCESS = "success"
    YES = "Yes"
    NO = "No"

    TOKEN_BUTTON = "TOKEN"
    INSTANCE_BUTTON = "Instance"

    TOKEN_QUESTION = "hatena"
    TOKEN_SEL_0 = "Set TOKEN"
    TOKEN_SEL_1 = "Select TOKEN"
    TOKEN_SET_WRITE_PLS = "Write TOKEN please"

    TOKEN_SEL_1_NO_USER = "No users."

    TOKEN_USER_SEL = "Select"
    TOKEN_NOW_USER_L = "L"
    TOKEN_NOW_USER_R = "R"
    TOKEN_USER_SELECT_DELETE = "Delete"
    TOKEN_USER_DEFAULT_SET = "Set to Default"

    TOKEN_NOW_USER_INFO = "Now User Info"
    TOKEN_SELECTED_INFO = "Selected TOKEN information:"
    TOKEN_USER_INSTANCE = INSTANCE_BUTTON
    TOKEN_USER_NAME = "UserName"
    TOKEN_USER_TOKEN = TOKEN_BUTTON

    TOKEN_SELECT_SUCCESS = "Select user successful!"
    TOKEN_SELECT_FAIL = "fail to select user"

    TOKEN_DELETED = "Deleted."
    TOKEN_DELETE_CHECK = "Are you sure about that?"

    TOKEN_DEFAULT_SETTED = "Setted to default user."

    TOKEN_ADD_SUCCESS = "TOKEN check successful!"
    TOKEN_ADD_FAIL = "TOKEN check fail."

    CHANGE_INSTANCE_HINT = "input instance such as 'misskey.io' 'misskey.backspace.fm'"
    OK_INSTANCE_CONNECT = "instance connected! :)"
    OK_INSTANCE_CONNECT_FAIL = "instance connect fail :("

    LANGUAGE_BUTTON = "Language"
    LANGUAGE_QUESTION = "Select language"
    LANGUAGE_RESET = "Reset"

    THEME_BUTTON = "Theme"
    THEME_QUESTION = "Select theme"
    THEME_DEFAULT = "default"
    THEME_MONO = "monochrome"
    THEME_GREEN = "green"
    THEME_BRIGHT = "bright"

    CLEAR_BUTTON = "Clear"

    CURRENT_BUTTON = "Current"
    CURRENT_INSTANCE = "Current Instance"
    CURRENT_TOKEN = TOKEN_BUTTON
    CURRENT_NAME = "Name"
    CURRENT_TOKENID = "TokenId"
    CURRENT_VALID = "Valid"
    CURRENT_INVALID = "Invalid"

    def __getattribute__(self, __name: str) -> Any:
        if __name == "value":
            return _(super().__getattribute__(__name))
        return super().__getattribute__(__name)
