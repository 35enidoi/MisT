from enum import Enum
from typing import Any

__all__ = ["NV_T"]

# NOTE:
# - i18nは MkAPIs.translation が gettext.install() を呼び、グローバル関数 _ を束縛する設計です。
# - 本ファイルの Enum は __getattribute__ で value アクセス時に _(value) を適用します。
# - ここにある簡易 fallback _ は、リンタ/テスト時に _ が未バインドでも落ちないための暫定で、
#   実行時は MkAPIs.translation によるグローバル _ のバインドに依存してください。

# リンター対策 + フォールバック定義
try:
    _  # type: ignore[name-defined]
except NameError:
    def _(x: Any) -> Any:  # type: ignore[override]
        return x


class NV_T(Enum):
    OK = "Ok"
    RETURN = "return"

    QUIT_BUTTON = "Quit"
    GET_NOTE_BUTTON = "Get note"
    PREV_NOTE_BUTTON = "Prev"  # 追加: 前のノートへ移動
    NEXT_NOTE_BUTTON = "Next"  # 追加: 次のノートへ移動
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
