# NOTE:
# i18n は MkAPIs.translation が gettext.install() を呼び、グローバル関数 _ を束縛する設計です。
# textenums (NV_T/CM_T) は各 Enum の __getattribute__ で value 参照時に _(value) を適用します。
# 実行環境で _ が未バインドな場合に備え、各ファイルに簡易フォールバック _ を定義していますが、
# 実運用では MkAPIs.translation によるグローバル _ のバインドに依存してください。

from .noteview_txts import NV_T
from .cfgmenu_txts import CM_T


# 公開シンボル
__all__ = ["NV_T", "CM_T"]
