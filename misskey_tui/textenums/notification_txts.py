from enum import Enum
from typing import Any

__all__ = ["NF_T"]

# リンター対策の定義
_:None

class NF_T(Enum):
    RETURN = "return"
    SUCCESS = "success"
    OK = "Ok"

    WINDOW_TITLE_NAME = "Notification"

    DEAFAULT_TXTBX_VAL = "Tab to change widget"

    GET_NTFY_PLS = "Please Get ntfy"

    FLAG_FOLLOW = "Follow"
    FLAG_MENTION = "Mention"
    FLAG_NOTE = "Note"
    FLAG_RP = "Reply"
    FLAG_QT = "Quote"
    FLAG_RN = "Renote"
    FLAG_REACTION = "Reaction"

    BT_GET_NTFY = "Get ntfy"
    BT_CLEAR = "Clear"
    BT_ALL = "All"
    BT_FOLLOW = FLAG_FOLLOW
    BT_MENTION = FLAG_MENTION
    BT_NOTE = FLAG_NOTE
    BT_RP = FLAG_RP
    BT_QT = FLAG_QT
    BT_RN = FLAG_RN
    BT_REACTION = FLAG_REACTION
    BT_SEL = "Select"

    GETNTFY_FAIL_TO_GET_TXTBX = "Fail to get notifications"
    GETNTFY_FAIL_TO_GET = "Fail to get ntfy"

    NT_REACTION = "{} was reaction [{}]"
    NT_RN = "{} was renoted"
    NT_RP = "{} was reply"
    NT_QT = "{} was quoted"
    NT_FOLLOW = "Follow comming!"
    NT_MENTION = "mention comming!"

    SELECT_SEL_FROM = "select from"

    SELECT_NOTE = "Select note\n"
    SELECT_NOTE_TYPE_MENTION = "type:mention\n"
    SELECT_NOTE_TYPE_RP = "type:reply\nfrom noteid:{}\n     txt:{}\n\n"
    SELECT_NOTE_TYPE_QT = "type:quote\nfrom noteid:{}\n     txt:{}\n\n"
    SELECT_NOTE_USER = "name:{}\nusername:{}\n"
    SELECT_NOTE_NOTE = "noteid:{}\ntxt:{}\n"
    SELECT_NOTE_FILES = "{} files"

    RN_CHECK = "Renote this?\nnoteId:{}\nname:{}\ntext:{}"

    REACTION_FROM = "reaction from note or deck or search?"
    REACTION_FROM_NOTE = "note"
    REACTION_FROM_DECK = "deck"
    REACTION_FROM_SEARCH = "search"

    REACTION_DECK_CREATE_PLS = "Please create reaction deck"

    REACTION_NOTE_THEREISNT = "there is no reactions"

    RN_CREATE_SUCCESS = "Create success! :)"
    RN_CREATE_FAIL = "Create fail :("

    REACTION_CREATE_SUCCESS = RN_CREATE_SUCCESS
    REACTION_CREATE_FAIL = RN_CREATE_FAIL

    def __getattribute__(self, __name: str) -> Any:
        if __name == "value":
            return _(super().__getattribute__(__name))
        return super().__getattribute__(__name)