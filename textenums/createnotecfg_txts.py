from enum import Enum
from typing import Any

__all__ = ["CNC_T"]

# リンター対策の定義
_:None

class CNC_T(Enum):
    RETURN = "return"
    OK = "Ok"

    BT_NOTE_VISIBLE = "notevisibility"
    BT_CW = "CW"
    BT_RENOTE_ID = "renoteId"
    BT_REPLY_ID = "replyId"

    NOTE_VISIBLE_POPTXT = BT_NOTE_VISIBLE
    NOTE_VISIBLE_PUBLIC = "Public"
    NOTE_VISIBLE_HOME = "Home"
    NOTE_VISIBLE_FOLLOWER = "Followers"

    OK_RN_SHOWNOTE = "user:{}\ntext:{}"
    OK_RN_SHOWNOTE_FAIL = "note show fail :(\nmaybe this noteId is unavailable"
    OK_RP_SHOWNOTE = OK_RN_SHOWNOTE
    OK_RP_SHOWNOTE_FAIL = OK_RN_SHOWNOTE_FAIL

    def __getattribute__(self, __name: str) -> Any:
        if __name == "value":
            return _(super().__getattribute__(__name))
        return super().__getattribute__(__name)