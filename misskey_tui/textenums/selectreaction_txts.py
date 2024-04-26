from enum import Enum
from typing import Any

__all__ = ["SR_T"]

# リンター対策の定義
_: None


class SR_T(Enum):
    RETURN = "return"
    OK = "Ok"

    NO_DB = "DB is None, Please GetDB."

    BT_GET_DB = "GetDB"

    SELECT_REACTION_CREATE_SUCCESS = "Create success! :)"
    SELECT_REACTION_CREATE_FAIL = "Create fail :("

    SELECT_DECKADD_ALREADY_IN_DECK = "this reaction already in deck"
    SELECT_DECKADD = "reaction added\nname:{}"

    GETDB_FAIL = "GetDB fail :("
    GETDB_SUCCESS = "GetDB success!"

    def __getattribute__(self, __name: str) -> Any:
        if __name == "value":
            return _(super().__getattribute__(__name))
        return super().__getattribute__(__name)
