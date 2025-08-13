# ViewModel → Model 移管計画（ノート状態・購読TL）

## 目的
- ViewModel の責務を UI ロジック中心にスリム化。
- Model 側でノート取得・保持・ナビゲーション（現在位置/前後可否/クリア）を一元管理。
- 変更通知により ViewModel → View の更新を安定化。

## 対象範囲（移管する責務）
- NoteViewModel の状態
  - notes: list[Note] → Model
  - notes_point: int → Model
  - TL: Literal["HTL","LTL","STL","GTL"] → Model
- ノート取得 / TL 切替ロジック → Model
- 前後ナビゲーション（next/prev、has_prev/has_next） → Model
- ViewModel に残すもの
  - View 連携（ポップアップ、テキスト描画、ボタン有効/無効）
  - 表示整形関数 `_note_inp`（第1段階はそのまま。将来 Presenter 層へ）

## 新規コンポーネント（Model 内）
- TimelineService（仮称）: TL/ノート/カーソルを管理するストア＋取得サービス
  - 所在: `misskey_tui/model/timeline.py`（または既存 `model.py` 内に追加でも可）
  - 依存: `MkAPIs`（`misskeypy_wrapper`, `mk`, `theme/lang/instance` 参照）

### 公開 API（案）
- プロパティ
  - `current_tl: Literal["HTL","LTL","STL","GTL"]`
  - `notes: list[Note]`（読み取り専用想定）
  - `index: int`（現在位置、読み取り専用想定）
  - `has_prev: bool`, `has_next: bool`
  - `current_note: Note | None`, `count: int`
- メソッド
  - `set_tl(tl) -> None`
  - `refresh(limit: int = 10) -> FetchResult`（成功/失敗・理由）
  - `clear() -> None`
  - `move_next() -> bool`, `move_prev() -> bool`
- 変更通知（Observer）
  - `add_on_change(handler)` / `remove_on_change(handler)`
  - `ChangeEvent` 例: `kind: Literal["notes","index","tl","cleared","error"]`（必要に応じて payload）

### 取得実装
- TL→API マッピングは TimelineService 内にカプセル化
- `misskeypy_wrapper` を利用（現行踏襲）
- 失敗時は `FetchResult` で理由を返却（トークン未設定、TL 不正、misskeypy 無効など）

## ViewModel の役割（移行後）
- Model から状態を読み出し、View へ反映
  - `note_write()` は `timeline.current_note` 等を使用
  - ボタン有効/無効は `timeline.has_prev / has_next` で決定
- ユーザー操作
  - 取得: `timeline.refresh()`
  - 前後: `timeline.move_prev()/move_next()`
  - TL 切替: `timeline.set_tl()`（UI 実装時）
- ポップアップ文言は `NV_T` を用いて ViewModel で対応（i18n）

## エラーハンドリング / i18n
- `TimelineService.refresh` は `FetchResult` を返す（`ok: bool`, `reason: Enum/str`）
- ViewModel は `FetchResult` に応じて `NV_T.*` でポップアップ
  - 例: トークン未設定→`NV_T.GET_NOTE_FAIL_ADDITIONAL_1`
  - TL 不正→`NV_T.GET_NOTE_FAIL_ADDITIONAL_2`

## インスタンス変更フック
- 既存の `msk_.add_on_change_instance` で
  - `timeline.clear()` を呼ぶ
  - 変更通知で ViewModel が NOTE_NONE 表示＋ナビ無効化

## 段階的移行ステップ
1. TimelineService を追加
   - 現 `NoteViewModel` の `notes/notes_point/TL` と取得・移動ロジックを移植
   - `add_on_change` でイベント発火
2. `MkAPIs` に `timeline` を組み込み
   - `self.timeline = TimelineService(self)`
   - インスタンス変更時に `timeline.clear()`
3. `NoteViewModel` 差し替え
   - 自前の `notes/notes_point/TL` を撤去し `self.msk_.timeline` 参照に置換
   - `next_note/prev_note` → `move_next/move_prev`
   - `note_get` → `refresh`
   - `update_nav_buttons` → `has_prev/has_next` を参照
   - `recreate_*`/`_on_instance_change` で timeline 状態から UI 初期化
4. 表示整形 `_note_inp`
   - 当面据え置き。将来 `NotePresenter`（util/presenter）へ抽出して単体テスト容易化
5. テスト
   - TimelineService 単体: TL 切替、取得成功/失敗、移動境界、clear
   - ViewModel 結合: ボタン有効/無効、ポップアップ分岐
6. 将来拡張（任意）
   - 非同期取得（Thread/Queue）＋メインスレッド反映
   - ページング（次ページ取得）/ スクロール
   - TL 選択 UI 追加、設定永続化（TL 記憶）

## 受け入れ基準
- ノート未取得時に Prev/Next が無効
- 取得後、位置・件数に応じて Prev/Next が正しく切替
- TL 切替で notes がリセットされ、取得が正しく動作
- インスタンス変更時に状態クリア＋UI 反映
- 既存 `NV_T` メッセージがそのまま機能

## シグネチャ例
```python
class TimelineService:
    def __init__(self, msk: MkAPIs): ...
    def set_tl(self, tl: Literal["HTL","LTL","STL","GTL"]) -> None: ...
    def refresh(self, limit: int = 10) -> FetchResult: ...
    def move_next(self) -> bool: ...
    def move_prev(self) -> bool: ...
    @property
    def has_prev(self) -> bool: ...
    @property
    def has_next(self) -> bool: ...
    @property
    def current_note(self) -> Note | None: ...
    def clear(self) -> None: ...
    def add_on_change(self, cb): ...
    def remove_on_change(self, cb): ...
```
