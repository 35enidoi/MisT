from enum import Enum
from typing import Any

__all__ = ["NV_T"]

# リンター対策の定義
_:None

class NV_T(Enum):
    OK = "Ok"
    RETURN = "return"
    SUCCESS = "success"
    ERROR_OCCURED = "something occured"

    WELCOME_MESSAGE = "or welcome to MisT!\nTab to change widget"
    QUIT = "Quit?"

    BT_QUIT = "Quit"
    BT_MOVE_L = "Move L"
    BT_MOVE_R ="Move R"
    BT_NOTE_UP = "Noteupdate"
    BT_NOTE_GET = "Note Get"
    BT_MORE = "More"
    BT_CFG = "Config"

    SEL_NOTE_CONNECT_FAIL = "connect failed.\nPlease Instance recreate."
    SEL_NOTE_POPTXT = "note get from"
    SEL_NOTE_POP_LATEST = "latest"
    SEL_NOTE_POP_UNTIL = "until"
    SEL_NOTE_POP_SINCE = "latest"
    SEL_NOTE_NOT_AVAILABLE = "get note please(latest)"

    MORE_POPTXT = "?"
    MORE_CREATE_NOTE = "Create Note"
    MORE_RN = "Renote"
    MORE_RP = "Reply"
    MORE_REACTION = "Reaction"
    MOREE_NOTIFI = "Notification"

    MORE_SEL_GET_NOTE_PLS = "Please Note Get"
    MORE_SEL_QT = "Quote"
    MORE_SEL_RN_OR_QT = "Renote or Quote?"
    MORE_SEL_REACTION_FROM = "reaction from note or deck or search?"
    MORE_SEL_FROM_NOTE = "note"
    MORE_SEL_FROM_DECK = "deck"
    MORE_SEL_FROM_SEARCH = "search"

    SEL_REAC_FROM_DECK_NODECK = "Please create reaction deck"

    SEL_REAC_FROM_NOTE_NOREAC = "there is no reactions"

    SEL_RN_NOTE_VAL = "Renote this?\nnoteId:{}\nname:{}\ntext:{}"

    def __getattribute__(self, __name: str) -> Any:
        if __name == "value":
            return _(super().__getattribute__(__name))
        return super().__getattribute__(__name)