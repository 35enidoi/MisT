# MkAPIs ラッパーとしての Model クラス設計計画

目的
- 既存の MkAPIs を「アプリのドメイン Model」から明確に分離し、`Model` クラスがアプリ状態の中核を担う。
- 以降は ViewModel などの呼び出し側は `Model` 経由（`model.mkapi` や `model.timeline`）で機能にアクセス。
- 将来的な機能追加（キャッシュ・非同期・設定永続化）を `Model` に集約しやすくする。

概要
- `Model` は MkAPIs の薄いラッパーではなく、アプリ状態を束ねるファサード。
- `Model.mkapi` に生の MkAPIs を保持しつつ、`Model.timeline` にタイムライン管理（取得/移動/状態保持）を提供。
- インスタンス変更などクロスカットなイベントは `Model` が受けて、配下へ伝搬・自分でも通知する。

新規/更新ファイル構成（案）
- `misskey_tui/model/model.py` ・・・ 新規 `Model` クラス
- `misskey_tui/model/timeline.py` ・・・ 新規 `TimelineService`（前計画のとおり）
- `misskey_tui/model/__init__.py` ・・・ エクスポート（`from .model import Model` など）
- 既存 `misskey_tui/model.py`（MkAPIs 定義元）・・・ そのまま。`Model` はこれを内包する

Model クラスの役割
- アプリ全体状態の集約点
  - MkAPIs の参照を `mkapi` として保持
  - タイムラインのストア/サービスを `timeline` として保持
  - 言語・テーマ・インスタンスなど、UI が参照する読み取り系プロパティを橋渡し
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

    # 読み取り系プロパティの橋渡し
    @property
    def lang(self) -> str: return self.mkapi.lang
    @property
    def theme(self): return self.mkapi.theme
    @property
    def instance(self) -> str: return self.mkapi.instance

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

TimelineService の要点（再掲）
- `current_tl`, `notes`, `index`, `has_prev/has_next`, `current_note`, `refresh`, `move_prev/next`, `clear`
- `misskeypy_wrapper` は `self.model.mkapi.misskeypy_wrapper` を介して呼ぶ
- 変更時は自身の `add_on_change` で通知。`Model` は必要ならそれを横流し/集約通知

移行方針（NoteViewModel から）
1) 依存の差し替え
   - コンストラクタ引数: `msk: MkAPIs` → `model: Model`
   - フィールド: `self.msk_` → `self.model`
2) 呼び出し変更
   - 取得: `self.model.timeline.refresh(limit=10)`
   - 前後移動: `self.model.timeline.move_prev()/move_next()`
   - 有効/無効: `self.model.timeline.has_prev/has_next`
   - 表示: `self.model.timeline.current_note` と `self.model.instance` など
   - 既存の `self.msk_.misskeypy_wrapper` 参照は `self.model.mkapi.misskeypy_wrapper` に置換（ViewModel で直接触る場面は段階的に削減）
3) インスタンス変更
   - これまでの `self.msk_.add_on_change_instance` への登録は `Model` 側で完結
   - ViewModel は `model.add_on_change` を購読し、NOTE_NONE 表示やボタン無効化を行う

段階的実装ステップ
- Step 1: `TimelineService` を実装（既存計画のまま）
- Step 2: `Model` を作成し、`TimelineService` を内包。`MkAPIs` のインスタンス変更を中継
- Step 3: `NoteViewModel` の依存を `Model` に切替
- Step 4: 表示系の確認とリグレッション修正
- Step 5: テスト（Timeline 単体、Model 結合、ViewModel 結合）

受け入れ基準
- 既存のノート取得/移動挙動が維持される
- インスタンス変更時に `timeline` がクリアされ、UI が NOTE_NONE になり Prev/Next 無効
- ViewModel から MkAPIs を直接参照せず `model.*` 経由での参照に置換

備考
- 将来的に設定の永続化（選択 TL など）や非同期取得キューを `Model` に集約可能。
- `Model` は「アプリの状態・ハブ」として拡張余地を確保し、UI/データ取得の結合度を下げる設計とする。

## イベント型の明確化（events.py 追加）
型安全と補完向上のため、Model/Timeline の変更通知イベントを型として定義します。

- 目的
  - Observer のイベントを厳密な型で表現し、分岐を `kind` と `action` に限定。
  - 将来のイベント追加も Union に型を足すだけで拡張可能。
- 追加ファイル（新規）
  - `misskey_tui/model/events.py`

### 提案実装（雛形）
```python
# misskey_tui/model/events.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Callable, Literal, Any

# ひな形（抽象）
class AbstractChangeEvent(Protocol):
    kind: Literal["instance", "timeline", "error", "settings"]

# 具体イベント
@dataclass(frozen=True)
class InstanceChangeEvent:
    kind: Literal["instance"] = "instance"

@dataclass(frozen=True)
class TimelineChangeEvent:
    kind: Literal["timeline"] = "timeline"
    action: Literal["refresh", "index", "clear", "set_tl"] = "refresh"
    index: int | None = None
    count: int | None = None
    tl: Literal["HTL", "LTL", "STL", "GTL"] | None = None

@dataclass(frozen=True)
class ErrorChangeEvent:
    kind: Literal["error"] = "error"
    reason: str = "unknown"
    detail: dict[str, Any] | None = None

@dataclass(frozen=True)
class SettingsChangeEvent:
    kind: Literal["settings"] = "settings"
    key: str = ""
    value: Any = None

# 型エイリアス
ChangeEvent = InstanceChangeEvent | TimelineChangeEvent | ErrorChangeEvent | SettingsChangeEvent
ChangeHandler = Callable[[ChangeEvent], None]
```

### Model での使用例（型ヒント差し替え）
```python
# misskey_tui/model/model.py（抜粋）
from misskey_tui.model.events import ChangeEvent, ChangeHandler, InstanceChangeEvent

class Model:
    def __init__(self, mkapi: MkAPIs) -> None:
        self.mkapi = mkapi
        self._observers: list[ChangeHandler] = []
        self.timeline = TimelineService(self)
        # MkAPIs のインスタンス変更を橋渡し
        self.mkapi.add_on_change_instance(self._on_instance_change)

    def add_on_change(self, cb: ChangeHandler) -> None:
        self._observers.append(cb)

    def remove_on_change(self, cb: ChangeHandler) -> None:
        if cb in self._observers:
            self._observers.remove(cb)

    def _emit(self, ev: ChangeEvent) -> None:
        for cb in list(self._observers):
            cb(ev)

    def _on_instance_change(self) -> None:
        self.timeline.clear()
        self._emit(InstanceChangeEvent())
```

### TimelineService での使用例
```python
# misskey_tui/model/timeline.py（抜粋）
from misskey_tui.model.events import TimelineChangeEvent

# 取得成功時
self._emit(TimelineChangeEvent(action="refresh", count=len(self._notes)))

# インデックス移動時
self._emit(TimelineChangeEvent(action="index", index=self.index))

# TL 切替時
self._emit(TimelineChangeEvent(action="set_tl", tl=self.current_tl))

# クリア時
self._emit(TimelineChangeEvent(action="clear"))
```

この方式により、呼び出し側（例: ViewModel）は `kind` と `action` に基づく分岐で明確に処理でき、IDE 補完も効きます。
