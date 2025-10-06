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
        # TimelineService には mkapi のみ注入
        self.timeline = TimelineService(self.mkapi)
        # TimelineService に Model のエミッタをバインド（購読管理はModelのみ）
        self.timeline.bind_emitter(self._emit)
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

    # ---- イベント購読（Modelに集約） ----
    def add_on_change(self, cb: ChangeHandler) -> None:
        self._observers.append(cb)
    def remove_on_change(self, cb: ChangeHandler) -> None:
        if cb in self._observers: self._observers.remove(cb)
    def _emit(self, ev: ChangeEvent) -> None:
        for cb in list(self._observers):
            try:
                cb(ev)
            except Exception:
                # UI保護のため握り潰し（必要に応じてログ）
                pass

    def _on_instance_change(self) -> None:
        # 下位サービスへ伝搬
        self.timeline.clear()
        # 上位へも通知（Modelが発火元）
        self._emit(InstanceChangeEvent())
```

TimelineService の要点
- `current_tl`, `notes(読み取り専用: tuple)`, `index`, `has_prev/has_next`, `current_note`, `count`
- `refresh(limit)`/`move_prev()`/`move_next()`/`set_tl()`/`clear()` は状態操作のみを行う
- イベント購読APIは持たない（`add_on_change`等は無し）
- Model からバインドされたエミッタ関数を用いて、必要時にイベントを「発火のみ」する
- `misskeypy_wrapper` は `mkapi.misskeypy_wrapper` を介して呼ぶ（mkapiのみ注入）

取得実装（詳細）
- TL→API マッピングは TimelineService 内にカプセル化
- 取得には `misskeypy_wrapper` を使用（既存踏襲）
- 成否や詳細通知は、TimelineService がバインド済みエミッタでイベント発火、購読管理は Model が担当

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
    def __init__(self, mkapi: MkAPIs): ...  # mkapiのみ注入

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

    # 操作（購読管理はしない。必要時にバインド済みエミッタで発火）
    def set_tl(self, tl: Literal["HTL","LTL","STL","GTL"]) -> None: ...
    def refresh(self, limit: int = 10) -> bool: ...
    def move_next(self) -> bool: ...
    def move_prev(self) -> bool: ...
    def clear(self) -> None: ...

    # Model から受け取る単一エミッタのバインド（購読管理はModel側）
    def bind_emitter(self, emit: Callable[[ChangeEvent], None]) -> None: ...
```

## TimelineService クラス詳細仕様

### 🎯 役割と責務
- **タイムライン状態の中核管理**：現在のNoteViewModelが持っている `notes`, `notes_point`, `TL` の状態管理を統合
- **API呼び出しの抽象化**：TL種別→API マッピングを内部でカプセル化
- **状態操作のみに特化**：イベント購読は行わず、発火のみを担当

### 📊 保持する状態
```python
# 内部状態（プロパティで公開）
current_tl: Literal["HTL","LTL","STL","GTL"]  # 現在選択中のTL
notes: tuple[Note, ...]                       # 取得済みノート（読み取り専用）
index: int                                    # 現在位置（0ベース）
count: int                                    # ノート総数
has_prev: bool                                # 前のノートがあるか
has_next: bool                                # 次のノートがあるか  
current_note: Note | None                     # 現在表示中のノート
```

### 🔧 提供する操作
```python
# タイムライン操作
def set_tl(tl: Literal["HTL","LTL","STL","GTL"]) -> None:
    # TL切り替え + ノートクリア + イベント発火

def refresh(limit: int = 10) -> bool:
    # ノート取得 + 成否を返す + 詳細はイベントで通知
    
def move_next() -> bool:
    # インデックス+1 (範囲チェック付き)
    
def move_prev() -> bool:
    # インデックス-1 (範囲チェック付き)
    
def clear() -> None:
    # 全状態リセット
```

### 🔌 イベントシステム
```python
def bind_emitter(self, emit: Callable[[ChangeEvent], None]) -> None:
    # Modelから受け取った単一エミッタをバインド
    # 購読管理はModelが行い、TimelineServiceは発火のみ
```

### 🏗️ 内部実装の想定
```python
class TimelineService:
    def __init__(self, mkapi: MkAPIs):
        self._mkapi = mkapi
        self._current_tl: Literal["HTL","LTL","STL","GTL"] = "LTL"
        self._notes: list[Note] = []
        self._index: int = 0
        self._emit: Callable[[ChangeEvent], None] | None = None
    
    # TL→API関数のマッピング（内部でカプセル化）
    def _get_tl_function(self):
        mapping = {
            "HTL": self._mkapi.mk.notes_timeline,
            "LTL": self._mkapi.mk.notes_local_timeline, 
            "STL": self._mkapi.mk.notes_hybrid_timeline,
            "GTL": self._mkapi.mk.notes_global_timeline,
        }
        return mapping[self._current_tl]
    
    def refresh(self, limit: int = 10) -> bool:
        if not self._mkapi.is_valid_misskeypy:
            self._emit_error("misskeypy_invalid")
            return False
            
        api_func = self._get_tl_function()
        notes = self._mkapi.misskeypy_wrapper(api_func, limit=limit)
        
        if notes is not None:
            self._notes = notes
            self._index = 0
            self._emit_success("refresh", count=len(notes))
            return True
        else:
            self._emit_error("token_missing" if self._mkapi.now_user_info is None else "unknown")
            return False
```

### 🎨 現在のNoteViewModelとの違い
| 項目 | 現在のNoteViewModel | 計画のTimelineService |
|------|---------------------|----------------------|
| **状態保持** | `notes`, `notes_point`, `TL` | `notes`, `index`, `current_tl` |
| **API呼び出し** | `note_get_func()` で分岐 | `_get_tl_function()` で内包 |
| **イベント** | 直接ViewModelが処理 | イベント発火のみ、購読はModel |
| **UI更新** | 直接view更新 | 状態変更のみ、UI更新はViewModel |
| **エラー処理** | popup直接表示 | イベントで理由通知 |

### 🎯 設計思想
1. **単一責任**: タイムライン状態管理に特化
2. **疎結合**: UIに依存せず、純粋な状態操作
3. **テスタブル**: 副作用を分離し、単体テスト可能
4. **型安全**: 全てのプロパティ・メソッドが型付き

この `TimelineService` により、現在 `NoteViewModel` に散らばっているタイムライン関連の責務が整理され、将来的な拡張（キャッシュ、非同期処理など）も容易になります。

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
- Model（購読管理と一部発火）
  - インスタンス変更受信時: `InstanceChangeEvent()` を `_emit(...)`
- TimelineService（発火のみ。購読はしない）
  - 取得成功: `TimelineChangeEvent(action="refresh", count=len(self._notes))`
  - 取得失敗: `ErrorChangeEvent(reason=...)`
  - インデックス移動: `TimelineChangeEvent(action="index", index=self.index)`
  - TL 切替: `TimelineChangeEvent(action="set_tl", tl=self.current_tl)`
  - クリア: `TimelineChangeEvent(action="clear")`

発火/購読の実装例（Model 集約版）
```python
# Model 側（抜粋）
from misskey_tui.model.events import ChangeEvent, ChangeHandler

self._observers: list[ChangeHandler] = []
self.timeline = TimelineService(self.mkapi)
self.timeline.bind_emitter(self._emit)

# TimelineService 側（抜粋）
# self._emit は bind_emitter で渡された関数。未設定時はNo-Opにしておく
if self._emit:
    self._emit(TimelineChangeEvent(action="refresh", count=len(self._notes)))
```

注意事項
- イベントは呼び出しスレッド（通常は UI メインループ）で同期的に配信されます。購読側は重い処理を避けるか非同期化してください。
- 例外は Model の `_emit` 内で握り潰し（UIを落とさない）。必要に応じてログを追加。
- TimelineService は購読者リストを持たず、単一エミッタへの委譲のみを行います。

## 📊 実装進捗状況 (最終更新: 2025年 10月1日)

### ✅ 完了している部分
1. **基本的な Model クラス** - `misskey_tui/model/model.py`
   - `Model` クラスが作成済み
   - `MkAPIs` と `MisTConfig` の統合完了
   - 基本構造は計画通り

2. **イベントシステムの基盤** - `misskey_tui/model/events.py`
   - `UserChangeEventHandler` クラスが実装済み
   - スレッドセーフなイベント処理機能あり
   - 例外処理も組み込み済み

3. **MkAPIs の実装** - `misskey_tui/model/mkapi.py`  
   - インスタンス変更フック (`add_on_change_instance`) 実装済み
   - `misskeypy_wrapper` 機能あり
   - 既存の API ラッパー機能完成

### 🔄 部分的に完了している部分
1. **NoteViewModel の状態管理**
   - タイムライン状態 (`notes`, `notes_point`, `TL`) は `NoteViewModel` 内で管理されている
   - 前後移動機能 (`next_note()`, `prev_note()`) 実装済み
   - ナビゲーションボタン制御 (`update_nav_buttons()`) 実装済み

### ❌ 未実装の部分
1. **TimelineService クラス** - `misskey_tui/model/timeline.py`
   - **完全に未実装** (最優先実装対象)
   - 計画書で最も重要な部分が未作成

2. **計画書準拠のイベント型** - `misskey_tui/model/events.py`
   - 現在は `UserChangeEvent` のみ
   - 計画書の `TimelineChangeEvent`, `InstanceChangeEvent`, `ErrorChangeEvent` が未実装

3. **Model クラスの完全実装**
   - 現在の `Model` は基本的な初期化のみ
   - 計画書の `timeline` プロパティ、イベント購読機能が未実装

4. **NoteViewModel のリファクタリング**
   - まだ直接 `mkapi` に依存している
   - `Model` 経由でのアクセスに切り替わっていない

### 📈 進捗率の推定
**全体進捗: 約 25-30%**

- **Step 1 (TimelineService実装)**: **0%完了** ❌
- **Step 2 (Model作成)**: **40%完了** 🔄
- **Step 3 (NoteViewModel切り替え)**: **0%完了** ❌  
- **Step 4 (表示系確認)**: **0%完了** ❌
- **Step 5 (テスト)**: **0%完了** ❌

### 🎯 次に実装すべき優先順位
1. **最優先**: `TimelineService` クラスの完全実装
2. **次点**: 計画書準拠のイベント型の実装  
3. **その後**: `Model` クラスの完全実装
4. **最後**: `NoteViewModel` のリファクタリング
