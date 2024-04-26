from enum import Enum
from typing import Any

__all__ = ["CM_T"]

# リンター対策の定義
_: None


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

    TOKEN_SEL_MIAUTH_URL = "MiAuth URL"
    TOKEN_SEL_COPIED = "cliped!"

    TOKEN_SEARCH_LEFT = "L"
    TOKEN_SEARCH_RIGHT = "R"
    TOKEN_SEARCH_SEL = TOKEN_SELECT
    TOKEN_SEARCH_DEL = "Delete"
    TOKEN_SEARCH_SET = "Set def"
    TOKEN_SEARCH_UNSET = "unset def"

    TOKEN_SEARCH_MES_NAME = "name:{}"
    TOKEN_SEARCH_MES_INSTANCE = "instance:{}"
    TOKEN_SEARCH_MES_TOKEN = "token:{}..."

    TOKEN_SEARCH_HEADMES_SEL = "Select"
    TOKEN_SEARCH_HEADMES_DEL = "Delete this?"
    TOKEN_SEARCH_HEADMES_SET = "set to default?"
    TOKEN_SEARCH_HEADMES_LEFT = "Too Left"
    TOKEN_SEARCH_HEADMES_RIGHT = "Too Right"
    TOKEN_SEARCH_HEADMES_NO_DEFAULT = "default token is none"
    TOKEN_SEARCH_HEADMES_UNSET = "unset success!"

    TOKEN_SEARCH_SELECT_CONNECT_OK = "connect ok!"
    TOKEN_SEARCH_SELECT_CONNECT_FAIL = "connect fail :("

    MIAUTH_GET_SUCCESS = "MiAuth check Success!"
    MIAUTH_HELLO_USER = "Hello {}"
    MIAUTH_FAIL_TO_GET = "fail to get"
    MIAUTH_FAIL_TO_GET_USER = "fail to get userinfo :("
    MIAUTH_CHECK_FAIL = "MiAuth check Fail :(\ntry again?"
    MIAUTH_TRY_AGAIN = "try again"

    CHANGE_INSTANCE_DETECT_TOKEN = "TOKEN detect!\nchange instance will delete TOKEN.\nOk?"
    CHANGE_INSTANCE_HINT = "input instance such as 'misskey.io' 'misskey.backspace.fm'"
    CHANGE_INSTANCE_CURRENT_INSTANCE = "current instance:{}"

    OK_TOKEN_CHECK = "TOKEN check OK :)"
    OK_TOKEN_CHECK_FAIL = "TOKEN check fail :("
    OK_TOKEN_FAIL_TO_GET = MIAUTH_FAIL_TO_GET
    OK_TOKEN_FAIL_TO_GET_USER = MIAUTH_FAIL_TO_GET_USER
    OK_TOKEN_HELLO_USER = MIAUTH_HELLO_USER

    OK_INSTANCE_CONNECT = "instance connected! :)"
    OK_INSTANCE_CONNECT_FAIL = "instance connect fail :("
    OK_INSTANCE_FAIL_TO_GET_ICON = "error occured while get icon :("
    OK_INSTANCE_FAIL_TO_GET_META = "error occured while get meta :("
    OK_INSTANCE_CURRENT_INSTANCE = CHANGE_INSTANCE_CURRENT_INSTANCE

    LANG_NO_TRANSLATION_FILES = "there is no translation files."
    LANG_RESET = "reset"
    LANG_SELECT = "select language"

    def __getattribute__(self, __name: str) -> Any:
        if __name == "value":
            return _(super().__getattribute__(__name))
        return super().__getattribute__(__name)
