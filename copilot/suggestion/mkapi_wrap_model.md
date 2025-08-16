# MkAPIs ラッパーとしての Model クラス設計計画

目的
- 既存の MkAPIs を「アプリのドメイン Model」から明確に分離し、`Model` クラスがアプリ状態の中核を担う。
- 現状`NoteViewModel`が保持している`timeline`の状態を`model.timeline`に集約し、ViewModelの役割を明確化する。
- 以降は ViewModel などの呼び出し側は `Model` 経由（`model.mkapi` や `model.timeline`）で機能にアクセス。
- 将来的な機能追加（キャッシュ・非同期・設定永続化）を `Model` に集約しやすくする。

概要
- `Model` は MkAPIs の薄いラッパーではなく、アプリ状態を束ねるファサード。
- `Model.mkapi` に生の MkAPIs を保持しつつ、`Model.timeline` にタイムライン管理（取得/移動/状態保持）を提供。
- インスタンス変更などクロスカットなイベントは `Model` が受けて、配下へ伝搬・自分でも通知する。

新規/更新ファイル構成（案）
- `misskey_tui/model/model.py` ・・・ 新規 `Model` クラス
- `misskey_tui/model/timeline.py` ・・・ 新規 `TimelineService`（統合後の中核）
- `misskey_tui/model/events.py` ・・・ 変更通知イベント（型）
- `misskey_tui/model/__init__.py` ・・・ エクスポート（`from .model import Model` など）
- 既存 `misskey_tui/model.py`（MkAPIs 定義元）・・・ そのまま。`Model` はこれを内包する

Model クラスの役割
- アプリ全体状態の集約点
  - MkAPIs の参照を `mkapi` として保持
  - タイムラインのストア/サービスを `timeline` として保持
  - 言語・テーマは `Model` が保持（型は後で決める TODO）。インスタンスは `mkapi` を参照
- 変更通知（Observer）
  - `add_on_change`/`remove_on_change` を提供し、`TimelineService` や `MkAPIs` の重要イベントを 1 箇所から通知
  - 通知イベントは `misskey_tui/model/events.py` の型付きイベント（`ChangeEvent`/`ChangeHandler`）を使用
- インスタンス変更時の連携
  - `mkapi.add_on_change_instance` を `Model` が購読
  - 受信したら `timeline.clear()`、必要なら `Model` 自身も `kind="instance"` で通知

シグネチャ例
```python
# misskey_tui/model/model.py
from __future__ import annotations
from misskey_tui.model import MkAPIs  # 既存
from .timeline import TimelineService
from .events import ChangeEvent, ChangeHandler, InstanceChangeEvent

class Model:
    def __init__(self, mkapi: MkAPIs) -> None:
        self.mkapi = mkapi
        self._observers: list[ChangeHandler] = []
        self.timeline = TimelineService(self)
        # MkAPIs のインスタンス変更を橋渡し
        self.mkapi.add_on_change_instance(self._on_instance_change)
        # TODO: 型と初期化方針を決める（設定/永続化と連動）
        self._lang = "en"  # TODO: 型
        self._theme = None  # TODO: 型

    # 読み取り系プロパティ
    @property
    def lang(self):  # TODO: 型
        return self._lang

    @property
    def theme(self):  # TODO: 型
        return self._theme

    @property
    def instance(self) -> str:
        return self.mkapi.instance

    def add_on_change(self, cb: ChangeHandler) -> None:
        self._observers.append(cb)
    def remove_on_change(self, cb: ChangeHandler) -> None:
        if cb in self._observers: self._observers.remove(cb)
    def _emit(self, ev: ChangeEvent) -> None:
        for cb in list(self._observers):
            cb(ev)

    def _on_instance_change(self) -> None:
        # 下位サービスへ伝搬
        self.timeline.clear()
        # 上位へも通知
        self._emit(InstanceChangeEvent())
```

TimelineService の要点
- `current_tl`, `notes(読み取り専用: tuple)`, `index`, `has_prev/has_next`, `current_note`, `count`
- `refresh(limit)` は bool を返し、詳細はイベントで通知
- `move_prev() / move_next()`, `set_tl()`, `clear()`
- `misskeypy_wrapper` は `self.model.mkapi.misskeypy_wrapper` を介して呼ぶ
- 変更時は `TimelineChangeEvent` / 失敗時は `ErrorChangeEvent` を発火。`Model` は必要なら横流し

取得実装（詳細）
- TL→API マッピングは TimelineService 内にカプセル化
- 取得には `misskeypy_wrapper` を使用（既存踏襲）
- 戻り値は `bool`（成功/失敗）。UI 更新や詳細情報はイベント（`TimelineChangeEvent` / `ErrorChangeEvent`）で配信

ViewModel の役割（移行後）
- Model/Timeline の状態を反映
  - テキスト描画は `timeline.current_note` から
  - ボタン状態は `timeline.has_prev/has_next`
- ユーザー操作の委譲
  - 取得: `timeline.refresh()`
  - 前後: `timeline.move_prev()/move_next()`
  - TL 切替: `timeline.set_tl()`
- ポップアップは `NV_T` を用いて i18n 対応（`ErrorChangeEvent.reason` に応じて選択）

インスタンス変更フック
- `Model` が `mkapi` のインスタンス変更を購読
- 受信時に `timeline.clear()`→ ViewModel が NOTE_NONE とナビ無効化を反映

段階的実装ステップ
- Step 1: `TimelineService` を実装（本設計準拠）
- Step 2: `Model` を作成し、`TimelineService` を内包。`MkAPIs` のインスタンス変更を中継
- Step 3: `NoteViewModel` の依存を `Model` に切替
- Step 4: 表示系の確認とリグレッション修正
- Step 5: テスト（Timeline 単体、Model 結合、ViewModel 結合）

受け入れ基準
- ノート未取得時に Prev/Next が無効
- 取得後、位置・件数に応じて Prev/Next が正しく切替
- TL 切替で notes がリセットされ、取得が正しく動作
- インスタンス変更時に状態クリア＋UI 反映
- 既存 `NV_T` メッセージがそのまま機能

エラーハンドリング / i18n
- `TimelineService.refresh` の成否は `bool`。詳細はイベントで通知
  - トークン未設定→`ErrorChangeEvent(reason="token_missing")`
  - TL 不正→`ErrorChangeEvent(reason="invalid_tl")`
  - misskeypy 無効→`ErrorChangeEvent(reason="misskeypy_invalid")`

将来拡張（任意）
- 取得の非同期化（Thread/Queue）＋メインスレッド反映
- ページング（次ページ取得）/ スクロール
- TL 選択 UI の追加
- 設定の永続化（選択 TL など）

### TimelineService シグネチャ（確定案）
```python
class TimelineService:
    def __init__(self, model: Model): ...

    # 状態
    @property
    def current_tl(self) -> Literal["HTL","LTL","STL","GTL"]: ...
    @property
    def notes(self) -> tuple[Note, ...]: ...  # 読み取り専用
    @property
    def index(self) -> int: ...
    @property
    def count(self) -> int: ...
    @property
    def has_prev(self) -> bool: ...
    @property
    def has_next(self) -> bool: ...
    @property
    def current_note(self) -> Note | None: ...

    # 操作
    def set_tl(self, tl: Literal["HTL","LTL","STL","GTL"]) -> None: ...
    def refresh(self, limit: int = 10) -> bool: ...
    def move_next(self) -> bool: ...
    def move_prev(self) -> bool: ...
    def clear(self) -> None: ...

    # 変更通知
    def add_on_change(self, cb: ChangeHandler) -> None: ...
    def remove_on_change(self, cb: ChangeHandler) -> None: ...
```

イベント型の明確化（events.py 追加）
以下の内容で新規ファイル `misskey_tui/model/events.py` を作成することを前提にします。イベントはすべて型付きで扱い、IDE 補完と型安全を確保します。

```python
# misskey_tui/model/events.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Literal, Any, Optional, Union

# イベント識別は各 dataclass の kind (Literal) で行う

# Timeline のアクション種別
TimelineAction = Literal["refresh", "index", "clear", "set_tl"]

# インスタンス変更（例: 接続先インスタンスが変更された）
@dataclass(frozen=True)
class InstanceChangeEvent:
    kind: Literal["instance"] = "instance"

# タイムラインに関する変化（取得・インデックス移動・TL 切替・クリア）
@dataclass(frozen=True)
class TimelineChangeEvent:
    kind: Literal["timeline"] = "timeline"
    action: TimelineAction = "refresh"
    # index: 現在位置（index 移動時など）
    index: Optional[int] = None
    # count: ノート件数（refresh 成功時など）
    count: Optional[int] = None
    # tl: 選択中 TL（set_tl 時など）
    tl: Optional[Literal["HTL", "LTL", "STL", "GTL"]] = None

# 何らかのエラー（取得失敗などの理由伝達）
@dataclass(frozen=True)
class ErrorChangeEvent:
    kind: Literal["error"] = "error"
    reason: str = "unknown"
    detail: Optional[dict[str, Any]] = None

# 型エイリアス
ChangeEvent = Union[
    InstanceChangeEvent,
    TimelineChangeEvent,
    ErrorChangeEvent,
]
ChangeHandler = Callable[[ChangeEvent], None]
```

イベント発火ポイント（規約）
- Model
  - インスタンス変更受信時: `InstanceChangeEvent()` を `_emit(...)`
- TimelineService
  - 取得成功: `TimelineChangeEvent(action="refresh", count=len(self._notes))`
  - インデックス移動: `TimelineChangeEvent(action="index", index=self.index)`
  - TL 切替: `TimelineChangeEvent(action="set_tl", tl=self.current_tl)`
  - クリア: `TimelineChangeEvent(action="clear")`
  - 取得失敗など: `ErrorChangeEvent(reason="token_missing" | "invalid_tl" | "misskeypy_invalid", detail=...)`

発火/購読の実装例
```python
# Model 側（抜粋）
from misskey_tui.model.events import ChangeEvent, ChangeHandler, InstanceChangeEvent

self._observers: list[ChangeHandler] = []

def add_on_change(self, cb: ChangeHandler) -> None:
    self._observers.append(cb)

def remove_on_change(self, cb: ChangeHandler) -> None:
    if cb in self._observers:
        self._observers.remove(cb)

def _emit(self, ev: ChangeEvent) -> None:
    for cb in list(self._observers):
        try:
            cb(ev)
        except Exception:
            # 購読側の例外で通知ループを止めない（ログは必要に応じて）
            pass

# TimelineService 側（抜粋）
from misskey_tui.model.events import TimelineChangeEvent, ErrorChangeEvent

# 取得成功時
self._emit(TimelineChangeEvent(action="refresh", count=len(self._notes)))

# 取得失敗時（例）
self._emit(ErrorChangeEvent(reason="token_missing"))

# インデックス移動
self._emit(TimelineChangeEvent(action="index", index=self.index))

# TL 切替
self._emit(TimelineChangeEvent(action="set_tl", tl=self.current_tl))

# クリア
self._emit(TimelineChangeEvent(action="clear"))
```

注意事項
- イベントは呼び出しスレッド（通常は UI メインループ）で同期的に配信されます。購読側は重い処理を避けるか非同期化してください。
- 例外は `_emit` 内で握り潰す方針（UI を落とさないため）。必要に応じてログを追加してください。
- 文字列 Literal は固定のため、誤記を CI/type-check で検出可能です。
