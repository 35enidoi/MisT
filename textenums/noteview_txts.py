from enum import Enum
from typing import Any

__all__ = ["NV_T"]

# リンター対策の定義
_:None

class NV_T(Enum):
    BT_QUIT = "Quit"
    BT_MOVE_L = "Move L"
    BT_MOVE_R ="Move R"
    BT_NOTE_UP = "Noteupdate"
    BT_NOTE_GET = "Note Get"
    BT_MORE = "More"
    BT_CFG = "Config"

    def __getattribute__(self, __name: str) -> Any:
        if __name == "value":
            return _(super().__getattribute__(__name))
        return super().__getattribute__(__name)