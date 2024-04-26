from enum import Enum
from typing import Any

__all__ = ["CN_T"]

# リンター対策の定義
_: None


class CN_T(Enum):
    OK = "Ok"
    RETURN = "return"

    BT_NOTE_CREATE = "Note Create"
    BT_HUG_PUNCH = "hug punch"
    BT_EMOJI = "emoji"
    BT_MORE_CONF = "MoreConf"

    EMOJI_SEL_FROM = "emoji select from..."
    EMOJI_SEL_FROM_DECK = "deck"
    EMOJI_SEL_FROM_SEARCH = "search"
    EMOJI_CREATE_DECK_PLS = "Please create reaction deck"

    CREATE_NOTE_ARE_YOU_SURE_ABOUT_THAT = "Are you sure about that?"

    CREATE_NOTE_SUCCESS = "Create note success :)"
    CREATE_NOTE_FAIL = "Create note fail :("

    RETURN_MAIN_RENOTEID_DETECT = "renoteId detect!"
    RETURN_MAIN_REPLYID_DETECT = "replyId detect!"
    RETURN_MAIN_DELETE_ANNOUNCE = "if return, it will delete"
    RETURN_MAIN_CHECK = CREATE_NOTE_ARE_YOU_SURE_ABOUT_THAT

    def __getattribute__(self, __name: str) -> Any:
        if __name == "value":
            return _(super().__getattribute__(__name))
        return super().__getattribute__(__name)
