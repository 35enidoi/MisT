# TimelineChangeEvent 型定義の更新計画

## 目的
`misskey_tui/enum/events.py` の `TimelineChangeEvent` を計画書に準拠した形に更新する。
型安全性を保ちつつ、TimelineServiceからの各種イベントを適切に表現できるようにする。

## 対象ファイル
- `misskey_tui/enum/events.py` - イベント型定義の更新

## 現在の状態
```python
# misskey_tui/enum/events.py (現在)
class TimelineNormalChangeEvent(TypedDict):
    action: str  # not error
    reason: None
    detail: dict | None

class TimelineErrorChangeEvent(TypedDict):
    action: Literal["error"]
    reason: str
    detail: None

TimelineChangeEvent = TimelineNormalChangeEvent | TimelineErrorChangeEvent
```

## 更新後の型定義（シンプル版 - 推奨）

### 基本方針
- **フラットな構造**: TypedDictのネストを避け、直接プロパティとして定義
- **型安全性**: Literalで可能な限り型を制限
- **拡張性**: 将来的な機能追加に対応可能な設計

### 具体的な型定義

```python
# misskey_tui/enum/events.py (更新後)
from typing import TypedDict, Literal

# ========== TimelineChangeEvent の型定義 ==========

# 1. リフレッシュ成功イベント（ノート取得成功）
class TimelineRefreshSuccessEvent(TypedDict):
    action: Literal["refresh"]
    reason: None
    count: int      # 取得したノート数
    index: int      # リセット後の位置（通常0）

# 2. インデックス移動イベント（前後移動）
class TimelineIndexChangeEvent(TypedDict):
    action: Literal["index"]
    reason: None
    index: int      # 移動後の位置

# 3. TL切り替えイベント
class TimelineSetTLEvent(TypedDict):
    action: Literal["set_tl"]
    reason: None
    tl: Literal["HTL", "LTL", "STL", "GTL"]  # 新しいTL

# 4. クリアイベント（全リセット）
class TimelineClearEvent(TypedDict):
    action: Literal["clear"]
    reason: None

# 5. エラーイベント
class TimelineErrorEvent(TypedDict):
    action: Literal["error"]
    reason: Literal[
        "misskeypy_invalid",  # misskeypy未初期化
        "token_missing",      # トークンなし
        "invalid_tl",         # 不正なTL（HTL/STLでトークンなし）
        "unknown"             # その他のエラー
    ]
    tl: Literal["HTL", "LTL", "STL", "GTL"] | None  # エラー発生時のTL（オプション）

# TimelineChangeEvent の統合型
TimelineChangeEvent = (
    TimelineRefreshSuccessEvent |
    TimelineIndexChangeEvent |
    TimelineSetTLEvent |
    TimelineClearEvent |
    TimelineErrorEvent
)
```

## 各イベントの発火タイミングと使用例

### 1️⃣ TimelineRefreshSuccessEvent
**発火**: `TimelineService.refresh()` 成功時

**TimelineService での発火例**:
```python
if self.__emit:
    self.__emit({
        'action': 'refresh',
        'reason': None,
        'count': len(self.__notes),
        'index': 0
    })
```

**ViewModel での受信例**:
```python
def on_timeline_event(self, event: TimelineChangeEvent):
    if event['action'] == 'refresh' and event['reason'] is None:
        self.view.popup(NV_T.GET_NOTE_SUCCESS.value, [NV_T.OK.value])
        self.note_write()
```

---

### 2️⃣ TimelineIndexChangeEvent
**発火**: `move_next()` / `move_prev()` 成功時

**TimelineService での発火例**:
```python
if self.__emit:
    self.__emit({
        'action': 'index',
        'reason': None,
        'index': self.__index
    })
```

**ViewModel での受信例**:
```python
def on_timeline_event(self, event: TimelineChangeEvent):
    if event['action'] == 'index':
        self.note_write()  # 表示更新
```

---

### 3️⃣ TimelineSetTLEvent
**発火**: `set_tl()` でTL切り替え時

**TimelineService での発火例**:
```python
if self.__emit:
    self.__emit({
        'action': 'set_tl',
        'reason': None,
        'tl': self.__current_tl
    })
```

**ViewModel での受信例**:
```python
def on_timeline_event(self, event: TimelineChangeEvent):
    if event['action'] == 'set_tl':
        self.view.textbox.value = NV_T.NOTE_NONE.value
        self.update_nav_buttons()
```

---

### 4️⃣ TimelineClearEvent
**発火**: `clear()` で状態リセット時（主にインスタンス変更時）

**TimelineService での発火例**:
```python
if self.__emit:
    self.__emit({
        'action': 'clear',
        'reason': None
    })
```

**ViewModel での受信例**:
```python
def on_timeline_event(self, event: TimelineChangeEvent):
    if event['action'] == 'clear':
        self.view.textbox.value = NV_T.NOTE_NONE.value
        self.update_nav_buttons()
```

---

### 5️⃣ TimelineErrorEvent
**発火**: `refresh()` などでエラー発生時

**TimelineService での発火例**:
```python
# misskeypy無効
if self.__emit:
    self.__emit({
        'action': 'error',
        'reason': 'misskeypy_invalid',
        'tl': None
    })

# トークンなし（HTL/STL）
if self.__emit:
    self.__emit({
        'action': 'error',
        'reason': 'invalid_tl',
        'tl': self.__current_tl
    })

# トークンなし（LTL/GTL）
if self.__emit:
    self.__emit({
        'action': 'error',
        'reason': 'token_missing',
        'tl': self.__current_tl
    })
```

**ViewModel での受信例**:
```python
def on_timeline_event(self, event: TimelineChangeEvent):
    if event['action'] == 'error':
        if event['reason'] == 'misskeypy_invalid':
            self.view.popup(NV_T.GET_NOTE_MISSKEYPY_INVALID.value, [NV_T.OK.value])
        
        elif event['reason'] == 'token_missing':
            msg = NV_T.GET_NOTE_FAIL.value + "\n" + NV_T.GET_NOTE_FAIL_ADDITIONAL_1.value
            self.view.popup(msg, [NV_T.OK.value])
        
        elif event['reason'] == 'invalid_tl':
            tl = event.get('tl', '?')
            msg = NV_T.GET_NOTE_FAIL.value + "\n"
            msg += NV_T.GET_NOTE_FAIL_ADDITIONAL_2.value + f"; {tl}"
            self.view.popup(msg, [NV_T.OK.value])
        
        else:  # unknown
            self.view.popup(NV_T.GET_NOTE_FAIL.value, [NV_T.OK.value])
```

## エラー理由の判定ロジック（TimelineService.refresh内）

```python
def refresh(self, limit: int = 10) -> bool:
    # 1. misskeypy有効性チェック
    if not self.__mkapi.is_valid_misskeypy:
        if self.__emit:
            self.__emit({
                'action': 'error',
                'reason': 'misskeypy_invalid',
                'tl': None
            })
        return False
    
    # 2. ノート取得
    api_func = self._get_tl_function()
    notes = self.__mkapi.misskeypy_wrapper(api_func, limit=limit)
    
    if notes is not None:
        # 成功
        self.__notes = notes
        self.__index = 0
        if self.__emit:
            self.__emit({
                'action': 'refresh',
                'reason': None,
                'count': len(notes),
                'index': 0
            })
        return True
    else:
        # 失敗：理由を判定
        reason = 'unknown'
        
        # トークンがない場合
        if self.__mkapi.now_user_info is None:
            # HTL/STLはトークン必須なので invalid_tl
            if self.__current_tl in ('HTL', 'STL'):
                reason = 'invalid_tl'
            else:
                # LTL/GTLでもトークンがあった方がいい場合
                reason = 'token_missing'
        
        if self.__emit:
            self.__emit({
                'action': 'error',
                'reason': reason,
                'tl': self.__current_tl
            })
        return False
```

## 実装ステップ

### Step 1: 型定義の更新
- [ ] `misskey_tui/enum/events.py` を上記の型定義に更新
- [ ] 既存の `TimelineNormalChangeEvent` と `TimelineErrorChangeEvent` を置き換え
- [ ] インポートの調整（必要に応じて）

### Step 2: TimelineService の実装（別タスク）
- [ ] `TimelineService.refresh()` でイベント発火
- [ ] `TimelineService.move_next/prev()` でイベント発火
- [ ] `TimelineService.set_tl()` でイベント発火
- [ ] `TimelineService.clear()` でイベント発火

### Step 3: NoteViewModel の更新（別タスク）
- [ ] イベントハンドラーの実装
- [ ] エラー理由に応じたポップアップ表示
- [ ] 既存の `note_get()` からの移行

### Step 4: テスト
- [ ] 各イベントが正しく発火されるか
- [ ] ViewModelが適切に反応するか
- [ ] エラーケースが正しく処理されるか

## 代替案（detail フィールド活用版）

既存の構造を最大限活かす場合：

```python
class TimelineNormalChangeEvent(TypedDict):
    action: Literal["refresh", "index", "set_tl", "clear"]
    reason: None
    detail: dict | None  # 柔軟性を保つ

class TimelineErrorChangeEvent(TypedDict):
    action: Literal["error"]
    reason: Literal["misskeypy_invalid", "token_missing", "invalid_tl", "unknown"]
    detail: dict | None  # {'tl': str | None} など

TimelineChangeEvent = TimelineNormalChangeEvent | TimelineErrorChangeEvent
```

この場合の `detail` の中身：
- `action="refresh"`: `{'count': int, 'index': int}`
- `action="index"`: `{'index': int}`
- `action="set_tl"`: `{'tl': str}`
- `action="clear"`: `None`
- `action="error"`: `{'tl': str | None}`

**メリット**: 既存コードへの影響が少ない  
**デメリット**: 型安全性が低い（`detail`の中身が`dict`）

## 推奨
**シンプル版**（フラット構造）を推奨します。
理由：
1. 型安全性が高い（IDE補完が効く）
2. コードが読みやすい
3. mypy等の型チェッカーで検出しやすい
4. 将来的な保守性が高い

## 参考：既存のメッセージ定義
```python
# misskey_tui/textenums/noteview_txts.py より
NV_T.GET_NOTE_SUCCESS = "Succeed in getting note!"
NV_T.GET_NOTE_FAIL = "Something occured while get note."
NV_T.GET_NOTE_FAIL_ADDITIONAL_1 = "Probably because there is no token."
NV_T.GET_NOTE_FAIL_ADDITIONAL_2 = "Probably because select invalid TL"
NV_T.GET_NOTE_MISSKEYPY_INVALID = "misskeypy is invalid. reconnect instance please"
NV_T.NOTE_NONE = "Please get note."
```

## 完了条件
- [ ] `misskey_tui/enum/events.py` が更新され、新しい型定義が適用されている
- [ ] 型チェック（mypy）がエラーなく通る
- [ ] 既存の `TimelineChangeEventHandler` が新しい型で動作する
- [ ] 既存のコードで型エラーが発生していない

## 注意事項
- この計画は**型定義のみ**を扱う。実際のイベント発火処理は TimelineService 実装時に行う
- 既存の `UserChangeEvent` との整合性を保つ
- 後方互換性よりも型安全性を優先（破壊的変更OK）

## 関連タスク
- TimelineService の完全実装（別計画書）
- Model クラスの完全実装（別計画書）
- NoteViewModel のリファクタリング（別計画書）

---

**作成日**: 2025年10月1日  
**ステータス**: 未実装  
**優先度**: 高（TimelineService実装の前提条件）
