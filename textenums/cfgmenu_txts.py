from enum import Enum
from typing import Any

__all__ = ["CM_T"]

# リンター対策の定義
_:None

class CM_T(Enum):
    RETURN = "return"
    OK = "Ok"
    SUCCESS = "success"
    ERROR_OCCURED = "something occured"

    BT_CHANGGE_TL = "Change TL"
    BT_CHANGGE_THEME = "Change Theme"
    BT_REAC_DECK = "Reaction deck"
    BT_TOKEN = "TOKEN"
    BT_INSTANCE = "Instance"
    BT_CURRENT = "Current"
    BT_VERSION = "Version"
    BT_LANG = "Language"
    BT_CLR = "Clear"
    BT_REFRESH = "Refresh"

    VERSION_WRITE_BY = "write by {}"

    CURRENT_INSTANCE = "Instance:{}"
    CURRENT_TOKEN_NONE = "TOKEN:None"
    CURRENT_TOKEN_AVAILABLE = "TOKEN:Available"
    CURRENT_NAME = " name:{}"
    CURRENT_USER_NAME = " username:{}"

    REAC_DECK_SET_TOKEN_PLS = "Please set TOKEN"
    REAC_DECK_CHECK_OR_ADD = "check deck or add deck?"
    REAC_DECK_CHECK = "check deck"
    REAC_DECK_DEL = "del deck"
    REAC_DECK_ADD = "add deck"
    REAK_DECK_CREATE_DECK_PLS = "Please create reaction deck"

    TL_HTL = "HTL"
    TL_LTL = "LTL"
    TL_STL = "STL"
    TL_GTL = "GTL"

    TL_CHANGED = "change TL:{}"
    TL_TOKEN_REQUIRED = "{} is TOKEN required"

    THEME_DEFAULT = "default"
    THEME_MONO = "monochrome"
    THEME_GREEN = "green"
    THEME_BRIGHT = "bright"

    TOKEN_HOWTO_NOWINS = "How to?\ncurrent instance:{}"
    TOKEN_CREATE = "Create"
    TOKEN_SELECT = "Select"

    TOKEN_WRITE_PLS = "write your TOKEN"

    TOKEN_SEL_AUTH_OR_WRITE = "MiAuth or write TOKEN?"
    TOKEN_SEL_CREATE_PLS = "Create TOKEN please."

    MIAUTH_URL = "MiAuth URL"
    MIAUTH_COPIED = "cliped!"

    TOKEN_CREATE_LEFT = "L"
    TOKEN_CREATE_RIGHT = "R"
    TOKEN_CREATE_DEL = "Delete"
    TOKEN_CREATE_SET = "Set def"
    TOKEN_CREATE_UNSET = "unset def"

    def __getattribute__(self, __name: str) -> Any:
        if __name == "value":
            return _(super().__getattribute__(__name))
        return super().__getattribute__(__name)